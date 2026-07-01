package com.cc.backend.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "t_news")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class News {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(length = 64)
    private String source;

    @Column(length = 1024)
    private String title;

    @Column(length = 512)
    private String link;

    private LocalDateTime date;

    @Column(columnDefinition = "TEXT")
    private String data;

    @Column(nullable = false, length = 256)
    private String name;

    @Column(nullable = false, length = 64)
    private String type;

    private Integer hotscore;

    private Integer tarid;
}
