package com.cc.backend.config;

import com.cc.backend.filter.TokenAuthFilter;
import com.cc.backend.service.TokenService;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class FilterConfig {

    private final TokenService tokenService;

    public FilterConfig(TokenService tokenService) {
        this.tokenService = tokenService;
    }

    @Bean
    public FilterRegistrationBean<TokenAuthFilter> tokenAuthFilterRegistration() {
        FilterRegistrationBean<TokenAuthFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new TokenAuthFilter(tokenService));
        registration.addUrlPatterns("/data", "/data/*");
        registration.setOrder(1);
        return registration;
    }
}
