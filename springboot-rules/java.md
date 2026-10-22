# Java rules (language level)

Rules for Java itself, whatever the framework.

## J-01: Close resources with try-with-resources

- **Source:** *Effective Java*, 3rd edition (Joshua Bloch), Item 9, "Prefer try-with-resources to try-finally". Spring rule pack J-01 in the superproject's `docs/pipeline/spring-boot-rule-pack.md`.
- **Prose:** Open every `AutoCloseable` (streams, readers, writers, JDBC connections, statements, result sets, `Scanner`) in a try-with-resources statement. Don't close it by hand in a `finally` block, and don't leave it unclosed.

```java
// Good
try (InputStream in = Files.newInputStream(path)) {
    return digest.digest(in.readAllBytes());
}

// Bad
InputStream in = Files.newInputStream(path);
try {
    return digest.digest(in.readAllBytes());
} finally {
    in.close();
}
```

## J-02: Don't ignore exceptions

- **Source:** *Effective Java*, 3rd edition, Item 77, "Don't ignore exceptions": an empty catch block defeats the purpose of exceptions.
- **Prose:** Every `catch` block must handle the exception: recover, translate it into a meaningful exception, or record it where the caller can see it (for example in the validation errors returned to the caller). Never leave a catch block empty. If ignoring really is right, say why in a comment and name the variable `ignored`.

```java
// Good
try {
    pageSize = Integer.parseInt(value);
} catch (NumberFormatException e) {
    errors.add("pageSize must be a whole number");
}

// Bad
try {
    pageSize = Integer.parseInt(value);
} catch (Exception e) {
}
```

## J-03: Keep the cause of a broad catch; give callers a safe reason

- **Source:** SLF4J FAQ: logging keeps the stack trace "assuming the exception is the last parameter" <https://www.slf4j.org/faq.html>. OWASP Error Handling Cheat Sheet: error details "are logged server side for investigation, and not returned to the user".
- **Prose:**
  - When you catch `Exception`, `RuntimeException` or `Throwable` and turn it into your own result or message, keep the exception: log it with the exception as the last argument, or pass it as the cause of the exception you throw.
  - Never send `getMessage()` of such an exception, or of a dependency's exception (`RestClientException`, `DataAccessException`), to a caller: it can carry SQL, URLs or class names. Send a fixed reason instead.
  - The messages of your own validation exceptions are fine to return.

```java
// Good
private static final Logger log = LoggerFactory.getLogger(RenewalService.class);  // org.slf4j
...
} catch (RuntimeException e) {
    log.warn("renewal {} failed", id, e);  // exception last: stack trace kept
    failures.add(new Failure(id, "could not be renewed (server error)"));  // fixed, safe reason
}

// Bad
} catch (RuntimeException e) {
    failures.add(new Failure(id, e.getMessage()));  // nothing logged; the caller sees internal details
}
```
