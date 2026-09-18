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
    START([User Visits Site]) --> LAND[Landing / Public Site]
    LAND --> CHOICE{Has Account?}

    CHOICE -- No --> REG[Registration]
    CHOICE -- Yes --> LOGIN[Login]

    REG --> DEFAULT[Assign Default Role: Subscriber]
    DEFAULT --> LOGIN

    LOGIN --> AUTH{Credentials Valid?}
    AUTH -- No --> LOGIN
    AUTH -- Yes --> ROLE{Role?}

    ROLE -- Administrator --> ADMIN[Admin Dashboard]
    ROLE -- Editor --> EDITOR[Editor Dashboard]
    ROLE -- Writer --> WRITER[Writer Dashboard]
    ROLE -- Contributor --> CONTRIB[Contributor Dashboard]
    ROLE -- Subscriber --> SUB[Subscriber Dashboard]

    ADMIN --> CONTENT[(Content & Users)]
    EDITOR --> CONTENT
    WRITER --> CONTENT
    CONTRIB --> CONTENT
    CONTENT --> PUBLIC[Public Site]
    SUB --> PUBLIC

    classDef entry fill:#4A90E2,stroke:#1F3A5F,color:#fff
    classDef role fill:#9013FE,stroke:#4A0A85,color:#fff
    classDef pub fill:#E0E0E0,stroke:#666,color:#000
    class START,LAND,CHOICE,LOGIN,REG,DEFAULT,AUTH entry
    class ADMIN,EDITOR,WRITER,CONTRIB,SUB,ROLE role
    class PUBLIC,CONTENT pub
```


```mermaid
flowchart TD
    A([Start]) --> B{Has Account?}

    B -- No --> C[Registration Form]
    C --> D[Name, Email, Password, Phone]
    D --> E{Valid Input?}
    E -- No --> F[Show Errors] --> C
    E -- Yes --> G[Create Account]
    G --> H[Assign Default Role: Subscriber]
    H --> I[Send Verification]
    I --> J{Verified?}
    J -- No --> K[Resend Verification] --> I
    J -- Yes --> L[Login Page]

    B -- Yes --> L
    L --> M[Enter Credentials]
    M --> N{Valid?}
    N -- No --> O[Invalid Credentials] --> L
    N -- Yes --> P{Account Active?}
    P -- No --> Q[Suspended - Contact Admin]
    P -- Yes --> R{Role?}

    R -- Administrator --> S1[Admin Dashboard]
    R -- Editor --> S2[Editor Dashboard]
    R -- Writer --> S3[Writer Dashboard]
    R -- Contributor --> S4[Contributor Dashboard]
    R -- Subscriber --> S5[Subscriber Dashboard]

    classDef reg fill:#F5A623,stroke:#8B5A00,color:#fff
    classDef auth fill:#7ED321,stroke:#3B6B00,color:#fff
    classDef role fill:#9013FE,stroke:#4A0A85,color:#fff
    class C,D,E,F,G,H,I,J,K reg
    class L,M,N,O,P,Q auth
    class R,S1,S2,S3,S4,S5 role
```

```mermaid
flowchart TD
    A[Admin Dashboard] --> B[Manage Users]
    A --> C[Manage Roles & Permissions]
    A --> D[Site Settings]
    A --> E[Content Overview]
    A --> F[Analytics]
    A --> G[Audit Logs]

    B --> B1[Create User]
    B --> B2[Edit User]
    B --> B3[Deactivate / Delete]
    B1 --> B4[Assign Role]
    B2 --> B4

    C --> C1[Define Role]
    C --> C2[Edit Permissions]

    E --> E1[View All Articles]
    E1 --> E2[Edit / Delete Any]
    E1 --> E3[Override Status]

    F --> F1[Traffic Stats]
    F --> F2[Top Articles]
    F --> F3[User Activity]

    G --> G1[Who Did What & When]

    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    class A,B,C,D,E,F,G,B1,B2,B3,B4,C1,C2,E1,E2,E3,F1,F2,F3,G1 admin
```

```mermaid
flowchart TD
    A[Editor Dashboard] --> B[Review Queue]
    A --> C[Manage Published]
    A --> D[Categories & Tags]
    A --> E[Schedule Posts]

    B --> B1{Decision}
    B1 -- Approve --> B2[Publish]
    B1 -- Request Changes --> B3[Send to Writer]
    B1 -- Reject --> B4[Notify Writer]

    C --> C1[Edit Article]
    C --> C2[Unpublish]
    C --> C3[Archive]

    E --> E1[Set Publish Date/Time]

    classDef editor fill:#9013FE,stroke:#4A0A85,color:#fff
    class A,B,C,D,E,B1,B2,B3,B4,C1,C2,C3,E1 editor
```

```mermaid
flowchart TD
    A[Writer Dashboard] --> B[Create New Article]
    A --> C[My Articles]
    A --> D[Profile Settings]

    B --> B1[Add Title, Body, Media]
    B1 --> B2[Select Category / Tags]
    B2 --> B3{Save or Submit?}
    B3 -- Save --> B4[Save as Draft]
    B3 -- Submit --> B5[Submit for Review]
    B5 --> EQ[(Editor Queue)]

    C --> C1{Status}
    C1 -- Draft --> C2[Continue Editing]
    C1 -- Pending --> C3[Awaiting Review]
    C1 -- Published --> C4[View Live]
    C1 -- Rejected --> C5[Revise & Resubmit]
    C5 --> B5

    classDef writer fill:#50E3C2,stroke:#1F7A66,color:#000
    class A,B,C,D,B1,B2,B3,B4,B5,C1,C2,C3,C4,C5 writer
    class EQ fill:#FFF,stroke:#333,color:#000
```

```mermaid
flowchart TD
    A[Contributor Dashboard] --> B[Submit Article]
    A --> C[View Submission Status]
    A --> D[Profile]

    B --> B1[Fill Limited Fields]
    B1 --> B2[Submit for Review]
    B2 --> EQ[(Editor Queue)]

    C --> C1{Status}
    C1 -- Pending --> C2[Awaiting Review]
    C1 -- Approved --> C3[Published by Editor]
    C1 -- Rejected --> C4[Notified]

    classDef contrib fill:#F8E71C,stroke:#8B7D00,color:#000
    class A,B,C,D,B1,B2,C1,C2,C3,C4 contrib
    class EQ fill:#FFF,stroke:#333,color:#000
```

```mermaid
flowchart TD
    A[Subscriber Dashboard] --> B[Browse Articles]
    A --> C[Saved Articles]
    A --> D[Comment History]
    A --> E[Profile Settings]
    A --> F[Newsletter Preferences]

    B --> B1[Read Article]
    B1 --> B2{Engage?}
    B2 -- Comment --> B3[Post Comment]
    B2 -- Save --> B4[Bookmark]
    B2 -- Share --> B5[Share to Social]

    classDef sub fill:#B8E986,stroke:#4A7A1F,color:#000
    class A,B,C,D,E,F,B1,B2,B3,B4,B5 sub
```

```mermaid
flowchart TD
    A([Public Site]) --> B[Browse by Category]
    A --> C[Search Articles]
    A --> D[Latest News]

    B --> E[Read Full Article]
    C --> E
    D --> E

    E --> F{Want to Comment?}
    F -- Yes --> G[Login / Register]
    F -- No --> H([End])
    G --> I[Subscriber Dashboard]

    classDef pub fill:#E0E0E0,stroke:#666,color:#000
    class A,B,C,D,E,F,H pub
    class G,I fill:#9013FE,stroke:#4A0A85,color:#fff
```

```mermaid
sequenceDiagram
    participant W as Writer
    participant C as Contributor
    participant E as Editor
    participant A as Admin
    participant P as Public

    W->>W: Create Draft
    W->>E: Submit for Review
    C->>E: Submit for Review

    E->>E: Review Article

    alt Approved
        E->>P: Publish Article
        P->>P: Read & Comment
    else Changes Requested
        E->>W: Request Revision
        W->>E: Resubmit
    else Rejected
        E->>W: Notify Rejection
    end

    A->>A: Manage Roles & Audit Logs
```

```mermaid
flowchart LR
    subgraph Roles
        AD[Admin]
        ED[Editor]
        WR[Writer]
        CO[Contributor]
        SU[Subscriber]
    end

    subgraph Permissions
        P1[Manage Users]
        P2[Approve Articles]
        P3[Create Articles]
        P4[Edit Any Article]
        P5[Comment]
        P6[Read Content]
    end

    AD --> P1 & P2 & P3 & P4 & P5 & P6
    ED --> P2 & P3 & P4 & P5 & P6
    WR --> P3 & P5 & P6
    CO --> P3 & P5 & P6
    SU --> P5 & P6
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

## 
Project Status

Completed Work

The Egerton Advertiser newspaper management system has been fully developed, tested, and deployed. The completed system includes:

- Complete newspaper website and content management system (CMS)
- Custom administration panel
- Rich text editor for article creation and formatting
- Article, category, and publication management
- Scheduled publishing
- Advanced analytics and readership insights
- Advertisement management and tracking
- Newsletter campaign management
- REST API
- Push notifications
- SEO optimization and search-engine-friendly content structure
- Responsive and user-friendly interface
- User and administrative access controls
- Database and backend management
- Performance and scalability enhancements
- Production configuration and deployment
- Full system testing and verification on Render
- Successful testing and approval at egertonadvertiser.onrender.com

Following successful testing and approval, the completed system was deployed to the client's production domain:

https://egertonadvertiser.co.ke

Deployment Status

Development: Complete
Testing: Complete
Client Approval: Complete
Production Deployment: Complete
Live Website: egertonadvertiser.co.ke

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
