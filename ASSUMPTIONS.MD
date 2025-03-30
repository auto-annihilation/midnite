# Assumptions

The following assumptions were made during the development of this solution. In a real-world scenario, I would seek clarification on these requirements before implementation. However, given the nature of this exercise, I've outlined the assumptions and provided reasoning for the chosen approach.

---

## API Contract

- The `user_id` is only included in successful responses where alert rules are evaluated. Error responses (e.g., 400, 422, 500) do not include `user_id`, as these scenarios are unrelated to alerting behavior.
- If multiple alert conditions are met, all relevant alert codes are included in the response.
- It is assumed that "3 consecutive withdrawals" and "3 consecutive increasing deposits" cannot be triggered simultaneously, as this would require deposits and withdrawals to occur within the same sequence, which contradicts the definition of "consecutive."

---

## Data Types

- The `amount` field in the payload is a string (e.g., "42.00"), not a float or integer. To ensure precision, it is treated as a `Decimal` with two decimal places.
- The `t` field is an integer representing seconds, interpreted as a sequential event identifier or epoch timestamp. The lack of millisecond precision implies that multiple events cannot occur in the same second without ambiguity.
- For the purposes of this exercise, it is assumed that the `t` value represents the time at which a trusted service received the deposit, rather than a client-provided field. Accepting timestamps directly from clients could expose the system to security risks, such as timestamp manipulation in man-in-the-middle attacks.

---

## Behavioral

- The endpoint receives events sequentially in real-time order, ensuring `t` values are strictly increasing and unique. To support multiple events per second, the timestamp would require millisecond precision. Events are ordered within the database before processing so even if this was not the case, they should still be handled as long as they do not colide within the second (in which the order would not be guaranteed - without also using the `created_at` timestamp to track the time it was created within the database).
- Transactions are stored in memory during evaluation against the alert rules. Once validated, they are persisted as part of the audit trail.
- The balance of the account is not tracked, meaning that we do not validate on the current balance when making a withdraw for a user with no previous events.

---

## Rule-Specific

- For "3 consecutive withdrawals," the withdrawals must occur back-to-back without any deposits in between. The requirements do not specify that deposits should be ignored so they are not.
- For "3 consecutive increasing deposits," only deposit events are considered. Withdrawals are ignored, and a sequence of deposits that are equal or decreasing does not trigger this rule.
- The "accumulative deposit amount over a window of 30 seconds" is evaluated using a sliding window from the current event (`t`) back 30 seconds. Events outside this window are excluded.
- Withdrawals are not factored into the accumulative deposit calculation.
- If multiple deposits occur at the exact same second, they are all included in the 30-second sliding window calculation.

---

## Error Handling

- Invalid payloads (e.g., malformed or missing fields) are handled gracefully:
  - If a payload contains invalid data types, a `400 Bad Request` response is returned.
  - If required fields are missing, a `422 Unprocessable Entity` response is returned.
- Negative deposit or withdrawal amounts are out of scope. A `400 Bad Request` response is returned if an amount of zero or less is provided.
- If an unrecognized `type` is provided (not "deposit" or "withdraw"), a `400 Bad Request` response is returned.

---

## Concurrency

- Events are grouped by `user_id`, allowing concurrent processing for different users, provided events occur in different seconds.
- The system processes concurrent events up to the capacity supported by a single API instance.

---

## Curl Command

- The curl example assumes the server is running on `localhost` at port `5000`.
- The example assumes JSON payloads are accepted, and the `Content-Type: application/json` header is enforced.
