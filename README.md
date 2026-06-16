# Dami - Centralized Blood Donation Management Platform

Dami is a centralized blood donation management platform that connects hospitals and blood banks directly with eligible donors. It replaces the unstructured, ad-hoc blood requests circulating on social media with a secure, targeted alert system. When a hospital opens an urgent blood request, Dami automatically notifies only the donors whose blood type and city match the request - protecting patient privacy while ensuring the right donors are reached at the right time.

## Key Features

- **Smart Targeted Alerts:** Centralized matching by blood type and city ensures donors only see requests relevant to them.
- **Request Management:** Hospitals can create, edit, and track urgent blood requests with live progress tracking toward the required quantity of blood bags.
- **Health-Safety Enforcement:** Donor health profiles automatically track total donations and enforce a mandatory 90-day waiting period between donations to ensure compliance with health rules.
- **Privacy Protection:** Patient names remain hidden from donors and are visible only to the authorized hospital staff that created the request.
- **Role-Based Access Control:** Separate, secure login portals and distinct permissions for donors, hospitals, and platform administrators.
- **Real-Time AJAX Actions:** Donors can commit to a request and hospital staff can confirm donation completion instantly without page reloads.

## System Workflow

### Donor Flow

1. **Registration:** Donors register by providing their blood type, city, and contact details under a secure authentication system.
2. **Dashboard Overview:** Displays active requests matching the donor's profile, total donation counts, and real-time eligibility status.
3. **Commitment:** Donors click "I'm coming to donate" to commit to a specific open request. This action triggers an immediate update to the hospital's received-bags counter via AJAX without reloads.

### Hospital Flow

1. **Account Verification:** Hospitals register and verify their accounts to secure platform legitimacy.
2. **Request Management:** Authorized staff open blood requests specifying the target blood type, quantity of bags required, and the specific branch address.
3. **Confirmation and Automation:** Lab staff confirm sample collection with a single click. This automatically updates the donor's eligibility status, increments the request's fulfillment count, and closes the request once the target quantity is met.

## Technical Specifications

- **Backend Framework:** Django (Python) handles server-side routing, data validation, and business logic.
- **Database:** MySQL relational database provides structured storage for operational datasets.
- **Frontend UI:** Built using standard HTML, CSS (Bootstrap for responsive layout), and vanilla JavaScript.
- **Asynchronous Integration:** Native AJAX handles seamless status transitions for donor commitment and staff confirmations.
- **API Layer:** RESTful API architecture provides structured endpoints for CRUD operations and future feature expansions.
- **Security Layer:** Enforces encrypted password storage, CSRF token validation, and strict role-based access control rules.

## Database Architecture (ERD Summary)

The relational schema consists of five core entities structured to optimize data isolation and operational performance:

### Core Entities

- **User:** Houses central authentication profiles containing username, encrypted password, email, role (donor, hospital, admin), phone number, city, and blood type.
- **HospitalProfile:** Extends the User entity for hospital accounts, capturing the hospital name, license number, and verification status.
- **DonorProfile:** Tracks critical donor statistics including last donation date, total donation count, and computed availability status.
- **BloodRequest:** Logs transactional details for active hospital requests, containing hidden patient records, requested blood type, bags required, bags received, branch address, status, and creation timestamps.
- **DonationRecord:** Intermediates and records individual donation attempts, managing relationship states from initial commitment to final completion timestamps.

### Entity Relationships

- **User to HospitalProfile / DonorProfile:** `1:1` relationship mapping general accounts to specific functional profiles.
- **HospitalProfile to BloodRequest:** `1:N` relationship allowing a verified hospital to open multiple localized requests over time.
- **BloodRequest to DonationRecord:** `1:N` relationship aggregating multiple individual donor commitments under a specific emergency request.
- **DonorProfile to DonationRecord:** `1:N` relationship capturing historical contribution logs for an individual volunteer across various requests.
