# Spring Boot rules (framework level, Spring Boot 3.5 on Java 21)

Each rule gives its source, its requirement (**Prose**) and a Good and a Bad example.

## SB-01: Use constructor injection, not field injection

- **Source:** Spring Framework reference, "Constructor-based or setter-based DI?": "The Spring team generally advocates constructor injection, as it lets you implement application components as immutable objects and ensures that required dependencies are not null." <https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html>
- **Prose:** Give each Spring component its required dependencies as constructor parameters, stored in `final` fields. Don't put `@Autowired` (or `@Inject`, `@Resource`) on fields. Test classes may use `@Autowired` fields for test infrastructure such as `MockMvc`.

```java
// Good
@Service
class ProjectService {
    private final ProjectRepository projects;
    ProjectService(ProjectRepository projects) { this.projects = projects; }
}

// Bad
@Service
class ProjectService {
    @Autowired private ProjectRepository projects;
}
```

## SB-02: Configure Spring Security 6 with a `SecurityFilterChain` bean

- **Source:** Spring blog, "Spring Security without the WebSecurityConfigurerAdapter": "In Spring Security 5.7.0-M2 we deprecated the `WebSecurityConfigurerAdapter`, as we encourage users to move towards a component-based security configuration." It was removed in 6.0. <https://spring.io/blog/2022/02/21/spring-security-without-the-websecurityconfigureradapter>
- **Prose:** Configure HTTP security by declaring a `@Bean SecurityFilterChain` method that takes `HttpSecurity` and returns `http.build()`. Declare users with a `UserDetailsService` bean and passwords with a `PasswordEncoder` bean. Don't extend `WebSecurityConfigurerAdapter`; it no longer exists.

```java
// Good
@Bean
SecurityFilterChain api(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .httpBasic(Customizer.withDefaults());
    return http.build();
}

// Bad
class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override protected void configure(HttpSecurity http) throws Exception { ... }
}
```

## SB-03: Import `jakarta.*`, not `javax.*`

- **Source:** Spring Boot 3.0 Migration Guide: "Jakarta EE now uses `jakarta` packages rather than `javax`." <https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide>
- **Prose:** In Spring Boot 3, import persistence, servlet, validation, annotation and transaction types from `jakarta.*` (`jakarta.persistence.Entity`, `jakarta.validation.Valid`, `jakarta.servlet.http.HttpServletRequest`). JDK packages such as `javax.crypto` and `javax.sql` stay as they are.

```java
// Good
import jakarta.persistence.Entity;
import jakarta.validation.constraints.NotBlank;
// Bad
import javax.persistence.Entity;
import javax.validation.constraints.NotBlank;
```

## SB-04: Turn off open-session-in-view

- **Source:** Spring Boot reference, "Open EntityManager in View": Spring Boot registers the interceptor "to apply the 'Open EntityManager in View' pattern, to allow for lazy loading in web views. If you do not want this behavior, you should set `spring.jpa.open-in-view` to `false` in your `application.properties`." <https://docs.spring.io/spring-boot/reference/data/sql.html>. Vlad Mihalcea, *High-Performance Java Persistence*, describes open-session-in-view as an anti-pattern.
- **Prose:** Set `spring.jpa.open-in-view=false` in `application.properties` (or `application.yml`). Load everything a response needs inside the service's transaction and return DTOs, so nothing lazy-loads while the response is written.

```properties
# Good
spring.jpa.open-in-view=false
# Bad: the property is missing, so Spring Boot keeps the session open during rendering
```

## SB-05: Don't rely on `@Transactional` for a call from the same class

- **Source:** Spring Framework reference, "Using `@Transactional`": "In proxy mode (which is the default), only external method calls coming in through the proxy are intercepted. This means that self-invocation (in effect, a method within the target object calling another method of the target object) does not lead to an actual transaction at runtime even if the invoked method is marked with `@Transactional`." <https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html>
- **Prose:** If a method needs its own transaction (for example `REQUIRES_NEW` so one item's failure doesn't roll back the others), put it on a different bean and call it through that bean. A call from inside the same class, with or without `this.`, skips the transaction settings even though the method is annotated.

```java
// Good
@Service
class RenewalService {
    private final SubscriptionRenewer renewer;        // separate bean
    RenewalService(SubscriptionRenewer renewer) { this.renewer = renewer; }
    List<String> renewAll(List<Long> ids) {
        List<String> failures = new ArrayList<>();
        for (Long id : ids) {
            try {
                renewer.renew(id);                    // its own transaction
            } catch (RuntimeException e) {            // SB-13, J-03
                log.warn("renewal {} failed", id, e);
                failures.add(id + ": could not be renewed");
            }
        }
        return failures;
    }
}
@Service
class SubscriptionRenewer {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void renew(Long id) { ... }
}

// Bad
@Service
class RenewalService {
    void renewAll(List<Long> ids) { ids.forEach(this::renew); }
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void renew(Long id) { ... }                // never gets its own transaction
}
```

## SB-06: Avoid N+1 queries when loading related entities

- **Source:** Vlad Mihalcea: "The N+1 query problem happens when the data access framework executes N additional SQL statements to fetch the same data that could have been retrieved when executing the primary SQL query." <https://vladmihalcea.com/n-plus-1-query-problem/>; *High-Performance Java Persistence*.
- **Prose:** When a response needs related entities or aggregates (an author's books, a count or sum per parent), fetch them in one query: a `JOIN FETCH` query, an `@EntityGraph`, or a query that returns the aggregated DTO directly. Don't loop over results and touch a lazy relation (`author.getBooks()`, `book.getAuthor().getName()`) for each one.

```java
// Good
@Query("select distinct a from Author a join fetch a.books where a.country = :country")
List<Author> findWithBooksByCountry(String country);

// Bad
for (Author a : authors.findAll()) {
    total += a.getBooks().size();                    // one extra query per author
}
```

## SB-07: Use the Spring Security 6 authorization DSL

- **Source:** Spring Security 6.5 API: `HttpSecurity.authorizeRequests()` is "Deprecated, for removal ... For removal in 7.0. Use `authorizeHttpRequests(Customizer)` instead" <https://docs.spring.io/spring-security/site/docs/6.5.x/api/org/springframework/security/config/annotation/web/builders/HttpSecurity.html>. Method security: `@EnableMethodSecurity` and `<sec:method-security/>` "supercede `@EnableGlobalMethodSecurity`" <https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html>. `antMatchers`, `mvcMatchers` and `regexMatchers` were removed in Spring Security 6.0 (they don't compile against 6.5; checked on 2026-10-01).
- **Prose:** Inside the `SecurityFilterChain` bean, use `authorizeHttpRequests(auth -> auth.requestMatchers(...)...)` with the lambda DSL. Don't use `authorizeRequests()`, `antMatchers`, `mvcMatchers`, `regexMatchers`, or chain sections with `.and()`. Enable method security with `@EnableMethodSecurity`, not `@EnableGlobalMethodSecurity`.

```java
// Good
http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/editor/**").hasRole("EDITOR")
        .anyRequest().authenticated())
    .httpBasic(Customizer.withDefaults());

// Bad
http.authorizeRequests()
        .antMatchers("/editor/**").hasRole("EDITOR")
        .anyRequest().authenticated()
    .and().httpBasic();
```

## SB-08: Mock beans with `@MockitoBean`

- **Source:** Spring Boot 3.4 release notes: "`@MockBean` and `@SpyBean` have been deprecated in favor of `@MockitoBean` and `@MockitoSpyBean` in Spring Framework." <https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.4-Release-Notes>. The `MockBean` Javadoc marks it `@Deprecated(since="3.4.0", forRemoval=true)`.
- **Prose:** In Spring tests, replace a bean with a Mockito mock using `@MockitoBean` (`org.springframework.test.context.bean.override.mockito.MockitoBean`) and spy with `@MockitoSpyBean`. Don't use `@MockBean` or `@SpyBean`. Plain unit tests don't need Spring at all: construct the class with `Mockito.mock(...)` collaborators.

```java
// Good
@WebMvcTest(ShippingController.class)
class ShippingControllerTest {
    @MockitoBean ShippingService shipping;
}
// Bad
@MockBean ShippingService shipping;
```

## SB-09: Validate request bodies

- **Source:** Spring Framework reference, `@RequestBody`: "You can use `@RequestBody` in combination with `jakarta.validation.Valid` or Spring's `@Validated` annotation, both of which cause Standard Bean Validation to be applied. By default, validation errors cause a `MethodArgumentNotValidException`, which is turned into a 400 (BAD_REQUEST) response." <https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/requestbody.html>
- **Prose:** Put constraints (`@NotBlank`, `@Positive`, `@Email`, ...) on request DTO fields and annotate every `@RequestBody` parameter with `@Valid`, so bad input gets a 400 before it reaches the service.

```java
// Good
@PostMapping
ResponseEntity<ProjectDto> create(@Valid @RequestBody CreateProjectRequest request) { ... }
// Bad
@PostMapping
ResponseEntity<ProjectDto> create(@RequestBody CreateProjectRequest request) { ... }
```

## SB-10: Use `RestClient` for synchronous HTTP calls

- **Source:** Spring Framework reference, "REST Clients": "`RestTemplate` — synchronous client with template method API, now deprecated in favor of `RestClient`" (current reference) <https://docs.spring.io/spring-framework/reference/integration/rest-clients.html>; `RestClient` exists since Spring Framework 6.1, which Spring Boot 3.5 uses.
- **Prose:** Call other HTTP services with `RestClient`, built from the auto-configured `RestClient.Builder` bean with the base URL from configuration. Don't create a `RestTemplate` (or `new RestTemplate()`) in new code.

```java
// Good
@Component
class CarrierClient {
    private final RestClient http;
    CarrierClient(RestClient.Builder builder, @Value("${carrier.base-url}") String baseUrl) {
        this.http = builder.baseUrl(baseUrl).build();   // timeouts come from application.properties (SB-12)
    }
}
// Bad
private final RestTemplate rest = new RestTemplate();
```

## SB-11: Deny by default in `authorizeHttpRequests`

- **Source:** OWASP Top 10:2021 A01: "Except for public resources, deny by default." Spring Security 6.5 reference, "Authorize HttpServletRequests": "Each rule is considered in the order they were declared", and ERROR dispatches are authorized too <https://docs.spring.io/spring-security/reference/6.5/servlet/authorization/authorize-http-requests.html>.
- **Prose:**
  - Give `permitAll()` only to the paths the request makes public. The first rule that matches wins, so a rule for a narrower path comes before a broader one (a role rule for `/schedule/admin/**` before `permitAll()` for `/schedule/**`).
  - End the rules with `.anyRequest().authenticated()`. Never end them with `.anyRequest().permitAll()` or `.requestMatchers("/**").permitAll()`, which make every path you did not list public (a controller added later, for example), unless the request says every other path is public; then say so in REPORT.md.
  - If any path is public, make `.dispatcherTypeMatchers(DispatcherType.ERROR).permitAll()` the first rule. Without it, a 400 or 404 from a public path reaches an anonymous caller as 401.

```java
// Good
import jakarta.servlet.DispatcherType;

http.authorizeHttpRequests(auth -> auth
        .dispatcherTypeMatchers(DispatcherType.ERROR).permitAll()  // errors keep their 400/404
        .requestMatchers(HttpMethod.GET, "/schedule/**").permitAll()  // public: the request says so
        .requestMatchers("/editor/**").hasRole("EDITOR")
        .anyRequest().authenticated())  // everything else needs a login
    .httpBasic(Customizer.withDefaults());

// Bad
http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/editor/**").hasRole("EDITOR")
        .anyRequest().permitAll());  // every path not listed is open to anyone
```

## SB-12: Give every outbound HTTP client connect and read timeouts

- **Source:** Spring Boot 3.5 reference, "Calling REST Services": the properties "change defaults that will be applied to all clients", but with `RestClient.create()` "no auto-configuration or RestClientCustomizer is applied" <https://docs.spring.io/spring-boot/3.5/reference/io/rest-client.html>. Neither property has a default.
- **Prose:** For clients built from the auto-configured `RestClient.Builder` (SB-10), set both properties in `application.properties`, a few seconds each unless the request names values. A client you build yourself (`RestClient.create()`, `RestClient.builder()`) does not get them: set both timeouts on its request factory.

```properties
# Good
spring.http.client.connect-timeout=2s
spring.http.client.read-timeout=5s
# Bad: no property and no timeout in code, so one hung call blocks its caller forever
```

## SB-13: When items succeed or fail on their own, catch each item's failure in the caller

- **Source:** Spring Framework 6.2 reference, "Transaction Propagation": `REQUIRES_NEW` transactions "can commit or roll back independently", and a failure caught inside a joined transaction still ends in an `UnexpectedRollbackException` <https://docs.spring.io/spring-framework/reference/6.2/data-access/transaction/declarative/tx-propagation.html>. RFC 9110: 400 covers "malformed request syntax".
- **Prose:** This applies when one request or job handles a list of items and the request wants each item to succeed or fail on its own.
  - Loop in a method that is not `@Transactional`.
  - Put all of one item's work in one `try`: its checks, its remote calls (SB-14) and the call into the bean that saves it in its own transaction (SB-05). Catch `RuntimeException` there, in the caller, not inside the `@Transactional` method.
  - Report each failed item with a message that says whose fault it was: the item's (your own validation message) or the system's (a fixed message, with the exception logged, J-03).
  - A request body that cannot be parsed at all gets a 4xx or a reported failure, never a 500.

```java
// Good
public BatchResult recordAll(List<Reading> readings) {  // not @Transactional
    BatchResult result = new BatchResult();
    for (Reading r : readings) {
        try {
            Tariff tariff = tariffs.current(r.meterId());  // remote call, no transaction open (SB-14)
            readingWriter.save(r, tariff);  // REQUIRES_NEW on another bean (SB-05)
            result.ok(r);
        } catch (InvalidReadingException e) {
            result.error(r, e.getMessage());  // the item's fault: your own message
        } catch (RuntimeException e) {
            log.warn("reading {} failed", r.id(), e);
            result.error(r, "not recorded (server error)");  // the system's fault (J-03)
        }
    }
    return result;
}

// Bad
for (Reading r : readings) {
    Tariff tariff = tariffs.current(r.meterId());  // outside the try: one 503 fails the whole request
    try { readingWriter.save(r, tariff); }
    catch (IllegalArgumentException e) { result.error(r, e.getMessage()); }  // other failures escape
}
```

## SB-14: No remote calls inside a database transaction

- **Source:** Vlad Mihalcea, "Spring Transaction and Connection Management": a transaction, `readOnly` ones included, normally takes its database connection when it begins, so "if the service method ... calls an external web service, the connection will be held throughout all that time"; design the service layer "so that the transactional methods are called as late as possible" <https://vladmihalcea.com/spring-transaction-connection-management/>.
- **Prose:** Don't call another service over the network (an HTTP client, for example) from a `@Transactional` method, `readOnly` ones included, or from a class annotated `@Transactional`. Make the call first, where no transaction is open, and pass the result into a `@Transactional` method on another bean (SB-05).

```java
// Good: the remote call first, then a @Transactional method on another bean (SB-05)
Tariff tariff = tariffs.current(reading.meterId());
readingWriter.save(reading, tariff);

// Bad
@Transactional
public void save(Reading reading) {
    Tariff tariff = tariffs.current(reading.meterId());  // holds a connection while it waits on the network
    readings.save(new MeterReading(reading, tariff));
}
```
