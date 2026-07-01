package com.cc.backend.controller;

import com.cc.backend.service.DataService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
public class DataController {

    private final DataService dataService;

    public DataController(DataService dataService) {
        this.dataService = dataService;
    }

    @GetMapping("/data")
    public Map<String, Object> getData(@RequestParam("target") String target) {
        List<?> data = switch (target.toLowerCase()) {
            case "field" -> dataService.getAllFields();
            case "company" -> dataService.getAllCompanies();
            case "news" -> dataService.getAllNews();
            default -> List.of();
        };

        return Map.of(
                "code", 200,
                "target", target,
                "count", data.size(),
                "data", data
        );
    }
}
