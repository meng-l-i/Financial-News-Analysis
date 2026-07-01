package com.cc.backend.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

@Service
public class TokenService {

    private static final Logger log = LoggerFactory.getLogger(TokenService.class);
    private static final long DAY_MS = 24 * 60 * 60 * 1000L; // 1 day

    private final String secret;

    public TokenService(@Value("${app.token-secret}") String secret) {
        this.secret = secret;
    }

    public boolean isValid(String token) {
        if (token == null || token.isEmpty()) return false;

        long today = System.currentTimeMillis() / DAY_MS;

        // Accept today's token ± 1 day for clock skew
        for (long d = today - 1; d <= today + 1; d++) {
            if (token.equals(compute(d))) {
                return true;
            }
        }
        return false;
    }

    /** Get today's token (used by /login) */
    public String currentToken() {
        long today = System.currentTimeMillis() / DAY_MS;
        return compute(today);
    }

    private String compute(long dayWindow) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec keySpec = new SecretKeySpec(
                    secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(keySpec);
            byte[] hmac = mac.doFinal(String.valueOf(dayWindow).getBytes(StandardCharsets.UTF_8));
            return Base64.getUrlEncoder().withoutPadding().encodeToString(hmac);
        } catch (Exception e) {
            log.error("Token computation failed", e);
            return "";
        }
    }
}
