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
    A[Login] --> B{Role?}
    B --> C[Admin]
    B --> D[Editor]
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
