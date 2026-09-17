# The Egerton Advertiser

The Egerton Advertiser is a modern online newspaper and content management system (CMS) built with Django. The project is designed to provide a professional platform for publishing campus and community news while giving editors and administrators complete control through a custom dashboard.

Unlike WordPress-based newspaper websites, this project is being developed entirely from code, making it highly customizable, scalable, and easy to extend as new requirements emerge.

The system features role-based authentication and access control, ensuring that each user interacts only with the tools and content relevant to their role. Roles include:

Administrator — full system access; manages users, roles, site settings, and overall platform configuration.

Editor — reviews, approves, edits, and publishes articles submitted by writers; manages categories and content workflow.

Writer / Journalist — creates and submits articles, uploads media, and tracks the status of their submissions.

Contributor — submits content for review with limited publishing privileges.

Subscriber / Reader — views published content, comments, and receives updates.

Each role is assigned granular permissions through Django's authentication and authorization framework, so access to the dashboard, publishing tools, and administrative functions is tightly controlled. This role-based structure improves security, streamlines editorial workflows, and ensures accountability across the platform.

```mermaid
flowchart TD
    %% ============ ENTRY POINTS ============
    START([User Visits The Egerton Advertiser])
    START --> LAND[Landing / Public Site]
    LAND --> CHOICE{Has Account?}

    %% ============ REGISTRATION FLOW ============
    CHOICE -- No --> REG[Registration Page]
    REG --> REGFORM[Fill: Name, Email, Password, Phone]
    REGFORM --> REGVALID{Valid Input?}
    REGVALID -- No --> REGERR[Show Errors] --> REGFORM
    REGVALID -- Yes --> REGCREATE[Create User Account]
    REGCREATE --> DEFAULTROLE[Assign Default Role: Subscriber]
    DEFAULTROLE --> VERIFY[Email / Phone Verification]
    VERIFY --> VERIFYOK{Verified?}
    VERIFYOK -- No --> RESEND[Resend Verification] --> VERIFY
    VERIFYOK -- Yes --> LOGIN

    %% ============ LOGIN FLOW ============
    CHOICE -- Yes --> LOGIN[Login Page]
    LOGIN --> CREDS[Enter Email & Password]
    CREDS --> AUTH{Credentials Valid?}
    AUTH -- No --> LOGINERR[Invalid Credentials] --> LOGIN
    AUTH -- Yes --> ACTIVE{Account Active?}
    ACTIVE -- No --> SUSPENDED[Account Suspended - Contact Admin]
    ACTIVE -- Yes --> ROLE{Role?}

    %% ============ ROLE ROUTING ============
    ROLE -- Administrator --> ADMIN[Admin Dashboard]
    ROLE -- Editor --> EDITOR[Editor Dashboard]
    ROLE -- Writer --> WRITER[Writer Dashboard]
    ROLE -- Contributor --> CONTRIB[Contributor Dashboard]
    ROLE -- Subscriber --> SUB[Subscriber Dashboard]

    %% ============ ADMIN FLOW ============
    ADMIN --> A1[Manage Users]
    ADMIN --> A2[Manage Roles & Permissions]
    ADMIN --> A3[Site Settings]
    ADMIN --> A4[Content Overview]
    ADMIN --> A5[Analytics]
    ADMIN --> A6[Audit Logs]

    A1 --> A1a[Create User]
    A1 --> A1b[Edit User]
    A1 --> A1c[Deactivate / Delete User]
    A1a --> A1d[Assign Role]
    A1b --> A1d

    A2 --> A2a[Define Role]
    A2 --> A2b[Edit Permissions]

    A4 --> A4a[View All Articles]
    A4a --> A4b[Edit / Delete Any Article]

    %% ============ EDITOR FLOW ============
    EDITOR --> E1[Review Queue]
    EDITOR --> E2[Manage Published Articles]
    EDITOR --> E3[Manage Categories & Tags]
    EDITOR --> E4[Schedule Posts]

    E1 --> E1a{Decision}
    E1a -- Approve --> E1b[Publish Article]
    E1a -- Request Changes --> E1c[Send Back to Writer]
    E1a -- Reject --> E1d[Notify Writer]

    E2 --> E2a[Edit Article]
    E2 --> E2b[Unpublish]
    E2 --> E2c[Archive]

    %% ============ WRITER FLOW ============
    WRITER --> W1[Create New Article]
    WRITER --> W2[My Articles]
    WRITER --> W3[Profile Settings]

    W1 --> W1a[Add Title, Body, Media]
    W1a --> W1b[Select Category / Tags]
    W1b --> W1c{Save or Submit?}
    W1c -- Save --> W1d[Save as Draft]
    W1c -- Submit --> W1e[Submit for Review]
    W1e --> EDITORQUEUE[(Editor Review Queue)]

    W2 --> W2a{Status}
    W2a -- Draft --> W2b[Continue Editing]
    W2a -- Pending --> W2c[Awaiting Review]
    W2a -- Published --> W2d[View Live Article]
    W2a -- Rejected --> W2e[Revise & Resubmit]

    %% ============ CONTRIBUTOR FLOW ============
    CONTRIB --> C1[Submit Article]
    CONTRIB --> C2[View Submission Status]
    CONTRIB --> C3[Profile]

    C1 --> C1a[Fill Limited Fields]
    C1a --> C1b[Submit for Review]
    C1b --> EDITORQUEUE

    C2 --> C2a{Status}
    C2a -- Pending --> C2b[Awaiting Review]
    C2a -- Approved --> C2c[Published by Editor]
    C2a -- Rejected --> C2d[Notified]

    %% ============ SUBSCRIBER FLOW ============
    SUB --> S1[Browse Articles]
    SUB --> S2[Saved Articles]
    SUB --> S3[Comment History]
    SUB --> S4[Profile Settings]
    SUB --> S5[Newsletter Preferences]

    S1 --> S1a[Read Article]
    S1a --> S1b{Engage?}
    S1b -- Comment --> S1c[Post Comment]
    S1b -- Save --> S1d[Bookmark Article]
    S1b -- Share --> S1e[Share to Social]

    %% ============ PUBLIC ACCESS ============
    LAND --> PUBLIC[Public Read Access]
    PUBLIC --> P1[Browse by Category]
    PUBLIC --> P2[Search Articles]
    PUBLIC --> P3[Latest News]
    P1 --> P4[Read Full Article]
    P2 --> P4
    P3 --> P4
    P4 --> P5{Want to Comment?}
    P5 -- Yes --> LOGIN
    P5 -- No --> ENDPUB([End])

    %% ============ CONTENT LIFECYCLE ============
    W1e --> EDITORQUEUE
    C1b --> EDITORQUEUE
    EDITORQUEUE --> E1
    E1b --> PUBLISHED[(Published Articles)]
    PUBLISHED --> PUBLIC

    %% ============ LOGOUT ============
    ADMIN --> LOGOUT([Logout])
    EDITOR --> LOGOUT
    WRITER --> LOGOUT
    CONTRIB --> LOGOUT
    SUB --> LOGOUT
    LOGOUT --> START

    %% ============ STYLING ============
    classDef entry fill:#4A90E2,stroke:#1F3A5F,color:#fff
    classDef reg fill:#F5A623,stroke:#8B5A00,color:#fff
    classDef auth fill:#7ED321,stroke:#3B6B00,color:#fff
    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    classDef editor fill:#9013FE,stroke:#4A0A85,color:#fff
    classDef writer fill:#50E3C2,stroke:#1F7A66,color:#000
    classDef contrib fill:#F8E71C,stroke:#8B7D00,color:#000
    classDef sub fill:#B8E986,stroke:#4A7A1F,color:#000
    classDef public fill:#E0E0E0,stroke:#666,color:#000

    class START,LAND,CHOICE entry
    class REG,REGFORM,REGVALID,REGERR,REGCREATE,DEFAULTROLE,VERIFY,VERIFYOK,RESEND reg
    class LOGIN,CREDS,AUTH,LOGINERR,ACTIVE,SUSPENDED,ROLE auth
    class ADMIN,A1,A2,A3,A4,A5,A6,A1a,A1b,A1c,A1d,A2a,A2b,A4a,A4b admin
    class EDITOR,E1,E2,E3,E4,E1a,E1b,E1c,E1d,E2a,E2b,E2c editor
    class WRITER,W1,W2,W3,W1a,W1b,W1c,W1d,W1e,W2a,W2b,W2c,W2d,W2e writer
    class CONTRIB,C1,C2,C3,C1a,C1b,C2a,C2b,C2c,C2d contrib
    class SUB,S1,S2,S3,S4,S5,S1a,S1b,S1c,S1d,S1e sub
    class PUBLIC,P1,P2,P3,P4,P5,ENDPUB public
```

---

## Features

### Public Website

- Homepage with featured headlines
- Breaking news ticker
- Latest news section
- News categories
- Search functionality
- Responsive design
- Advertisement placements
- Newsletter subscription
- Author profiles
- Reader comments
- Contact page

### Admin Dashboard

- Custom admin dashboard
- User and role management
- Article management
- Category management
- Tag management
- Advertisement management
- Media library
- Newsletter management
- Contact message management
- Website analytics
- Site settings

---

## Technology Stack

- Python
- Django
- Bootstrap 5
- HTMX
- CKEditor
- SQLite (Development)
- PostgreSQL (Production)
- HTML5
- CSS3
- JavaScript

---

## Project Structure

```text
egerton_advertiser/
│
├── apps/
│   ├── accounts/
│   ├── dashboard/
│   ├── articles/
│   ├── categories/
│   ├── tags/
│   ├── comments/
│   ├── advertisements/
│   ├── media_library/
│   ├── newsletter/
│   ├── contacts/
│   ├── analytics/
│   ├── search/
│   ├── notifications/
│   └── settings_manager/
│
├── templates/
├── static/
├── media/
├── egerton_advertiser/
├── requirements.txt
└── manage.py
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/eKidenge/egerton_advertiser.git
```

### 2. Navigate into the project

```bash
cd egerton_advertiser
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Start the development server

```bash
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000/
```

---

## Current Status

The project is currently under active development. The main focus is building a robust newspaper content management system with a clean user experience and a powerful custom administration panel.

Upcoming features include:

- Rich text editor
- Scheduled publishing
- Advanced analytics
- Advertisement tracking
- Newsletter campaigns
- REST API
- Push notifications
- SEO optimization
- Performance enhancements

---

## Vision

The Egerton Advertiser aims to become a modern digital newspaper platform for the Egerton University community. Beyond serving as a news portal, the project is also an opportunity to demonstrate scalable Django development practices and build a flexible CMS that can grow with future needs.

---

## Contributing

Contributions, suggestions, and feedback are welcome. If you'd like to contribute, feel free to fork the repository, open an issue, or submit a pull request.

---

## License

This project is licensed under the MIT License.

---

**Developed by Elisha Kidenge**
