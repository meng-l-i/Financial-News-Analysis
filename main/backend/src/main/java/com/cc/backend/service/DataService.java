package com.cc.backend.service;

import com.cc.backend.model.Company;
import com.cc.backend.model.CompanyRepository;
import com.cc.backend.model.Field;
import com.cc.backend.model.FieldRepository;
import com.cc.backend.model.News;
import com.cc.backend.model.NewsRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class DataService {

    private final FieldRepository fieldRepository;
    private final CompanyRepository companyRepository;
    private final NewsRepository newsRepository;

    public DataService(FieldRepository fieldRepository,
                       CompanyRepository companyRepository,
                       NewsRepository newsRepository) {
        this.fieldRepository = fieldRepository;
        this.companyRepository = companyRepository;
        this.newsRepository = newsRepository;
    }

    @Transactional(readOnly = true)
    public List<Field> getAllFields() {
        return fieldRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<Company> getAllCompanies() {
        return companyRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<News> getAllNews() {
        return newsRepository.findByDateAfter(LocalDateTime.now().minusDays(5));
    }
}
