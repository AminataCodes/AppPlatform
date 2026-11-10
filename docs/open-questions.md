# AppPlatform — Open Questions

These decisions need the project owner's input before the design and implementation are frozen. Recommendations are provided to make the choices easier.

## 1. Visual direction

**Q1. Theme:** light, dark, or both?

Recommendation: light theme first; dark mode is optional and should not delay core functionality.

**Q2. Visual style:** restrained enterprise portal, or modern SaaS dashboard with more whitespace and cards?

Recommendation: restrained enterprise style with modern spacing and clear typography. The interface should feel like an internal technical tool, not a marketing website.

## 2. User and authentication

**Q3. Should V1 have no login, or a demonstrative login screen?**

Recommendation: no login. A fake login adds little value and can confuse the security story. Explain that real authentication is out of scope.

## 3. Demo data

**Q4. Keep the sample names `customer-api`, `payment-api` and `banking-portal`, or choose neutral names?**

Recommendation: keep these fictional examples if they make the platform scenario easy to understand. Do not imply they are actual BPCE applications.

## 4. Failure scenario

**Q5. Should the simulation produce deterministic outcomes or random outcomes?**

Recommendation: deterministic. For example, a known demo version can fail, so the success and failure paths can be demonstrated reliably.

## 5. Interface language

**Q6. French or English?**

Recommendation: choose the language in which the project can be demonstrated most fluently. Technical identifiers and status enums can remain in English.

## 6. Feature versus polish

**Q7. Prefer a highly polished interface with the three defined workflows, or more features with a simpler interface?**

Recommendation: prioritize UI/UX quality and the three workflows. This better matches the frontend UI/UX Angular target role.

## 7. Confirmation record

Record the answers here once decided:

- Theme:
- Visual style:
- Authentication:
- Demo application names:
- Failure scenario:
- Interface language:
- Feature/polish priority:
