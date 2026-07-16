package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"log/slog"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"os/signal"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	targetURL := getenv("API_INGESTION_URL", "http://localhost:8000")
	target, err := url.Parse(targetURL)
	if err != nil {
		logger.Error("invalid API_INGESTION_URL", "error", err)
		os.Exit(1)
	}

	proxy := httputil.NewSingleHostReverseProxy(target)
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		logger.Error("proxy failed", "request_id", requestIDFrom(r), "error", err)
		http.Error(w, "downstream unavailable", http.StatusBadGateway)
	}

	router := chi.NewRouter()
	router.Use(middleware.RealIP)
	router.Use(requestIDMiddleware)
	router.Use(loggingMiddleware(logger))

	router.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, `{"status":"ok","service":"traffic-gateway"}`)
	})
	router.Get("/metrics", func(w http.ResponseWriter, r *http.Request) {
		writeText(w, http.StatusOK, "traffic_gateway_stub_info 1\n")
	})

	router.Post("/v1/predict", proxyHandler(proxy, target))
	router.Get("/v1/tasks/{taskID}", proxyHandler(proxy, target))
	router.Post("/v1/replay/{requestID}", func(w http.ResponseWriter, r *http.Request) {
		// TODO: load stored request from gateway DB and forward it again.
		writeJSON(w, http.StatusNotImplemented, `{"error":{"code":"NOT_IMPLEMENTED","message":"replay storage is not implemented yet"}}`)
	})

	server := &http.Server{
		Addr:              getenv("GATEWAY_ADDR", ":8080"),
		Handler:           router,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	go func() {
		logger.Info("traffic-gateway started", "addr", server.Addr, "target", target.String())
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = server.Shutdown(shutdownCtx)
}

func proxyHandler(proxy *httputil.ReverseProxy, target *url.URL) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		r.URL.Scheme = target.Scheme
		r.URL.Host = target.Host
		r.Host = target.Host
		r.Header.Set("X-Gateway-Timestamp", time.Now().UTC().Format(time.RFC3339Nano))
		r.Header.Set("X-Trace-ID", requestIDFrom(r))
		proxy.ServeHTTP(w, r)
	}
}

func requestIDMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := r.Header.Get("X-Request-ID")
		if requestID == "" {
			requestID = newID()
		}
		r.Header.Set("X-Request-ID", requestID)
		w.Header().Set("X-Request-ID", requestID)
		next.ServeHTTP(w, r)
	})
}

func loggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
			next.ServeHTTP(ww, r)
			logger.Info(
				"http_request",
				"request_id", requestIDFrom(r),
				"method", r.Method,
				"path", r.URL.Path,
				"status", ww.Status(),
				"latency_ms", time.Since(start).Milliseconds(),
				"body_size", r.ContentLength,
			)
		})
	}
}

func requestIDFrom(r *http.Request) string {
	return r.Header.Get("X-Request-ID")
}

func newID() string {
	var b [16]byte
	if _, err := rand.Read(b[:]); err != nil {
		return time.Now().UTC().Format("20060102150405.000000000")
	}
	return hex.EncodeToString(b[:])
}

func getenv(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}

func writeJSON(w http.ResponseWriter, status int, body string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_, _ = w.Write([]byte(body))
}

func writeText(w http.ResponseWriter, status int, body string) {
	w.Header().Set("Content-Type", "text/plain; version=0.0.4")
	w.WriteHeader(status)
	_, _ = w.Write([]byte(body))
}
