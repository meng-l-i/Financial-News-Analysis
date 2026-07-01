package com.cc.backend.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class UpdateController {

    @PostMapping("/update")
    public Map<String, Object> update() {
        return Map.of(
                "code", 200,
                "message", "Update endpoint - reserved for future implementation"
        );
    }
}
