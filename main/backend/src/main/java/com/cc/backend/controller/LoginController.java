package com.cc.backend.controller;

import com.cc.backend.service.TokenService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class LoginController {

    private final TokenService tokenService;

    public LoginController(TokenService tokenService) {
        this.tokenService = tokenService;
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody Map<String, String> body) {
        String username = body.getOrDefault("username", "");
        String password = body.getOrDefault("password", "");

        if ("root".equals(username) && "root".equals(password)) {
            String token = tokenService.currentToken();
            return Map.of(
                    "code", 200,
                    "message", "login success",
                    "token", token,
                    "expires_in", "24h"
            );
        }

        return Map.of(
                "code", 401,
                "message", "invalid credentials"
        );
    }
}
