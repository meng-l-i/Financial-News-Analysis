package com.cc.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.Map;

@RestController
public class HealthController {

    private final DataSource dataSource;

    public HealthController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        boolean dbOk = checkDatabase();

        return Map.of(
                "status", dbOk ? "UP" : "DEGRADED",
                "service", "cc-backend",
                "database", dbOk ? "CONNECTED" : "DISCONNECTED",
                "timestamp", System.currentTimeMillis()
        );
    }

    private boolean checkDatabase() {
        try (Connection conn = dataSource.getConnection()) {
            return conn.isValid(3);
        } catch (Exception e) {
            return false;
        }
    }
}
