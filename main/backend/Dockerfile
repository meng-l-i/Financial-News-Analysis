FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY settings-docker.xml /root/.m2/settings.xml
COPY pom.xml .
RUN mvn dependency:go-offline -q
COPY src ./src
RUN mvn package -DskipTests -q

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
COPY conf/ /app/conf/
RUN mkdir -p /app/data
EXPOSE 5070 5071
ENTRYPOINT ["java", "-jar", "app.jar", "--spring.config.location=file:./conf/application.yml"]
