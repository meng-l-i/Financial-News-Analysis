package com.cc.backend.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "t_field")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Field {

    @Id
    @Column(name = "field_id")
    private Integer fieldId;

    @Column(nullable = false, unique = true, length = 128)
    private String name;

    @Column(nullable = false)
    private Integer hotscore = 0;
}
