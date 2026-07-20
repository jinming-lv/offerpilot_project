# CareerPilot API Documentation

Version: v1.0

Base URL

http://localhost:8000/api

---

# 1. Resume Module

## 1.1 Upload Resume

POST /resume/upload

Description

Upload a PDF/DOCX resume and extract structured information.

Request

Content-Type:

multipart/form-data

Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | Resume PDF/DOCX |

Response

Status Code

200 OK

```json
{
  "success": true,
  "resume_id": "resume_001",
  "data": {
    ...
  }
}
```

---

# 2. Job Module

## 2.1 Analyze Job Description

POST /job/analyze

Description

Analyze job description.

Request

```json
{
    "job_text":"Python开发工程师..."
}
```

Response

```json
{
    "success":true,
    "job_id":"job_001",
    "data":{
        ...
    }
}
```

---

# 3. Match Module

POST /match

Description

Calculate resume-job matching score.

Request

```json
{
    "resume_id":"resume_001",
    "job_id":"job_001"
}
```

Response

```json
{
    "success":true,
    "data":{
        ...
    }
}
```

---

# 4. Interview Module

POST /interview/questions

Description

Generate interview questions.

Request

```json
{
    "resume_id":"resume_001",
    "job_id":"job_001",
    "difficulty":"medium"
}
```

Response

```json
{
    "success":true,
    "data":{
        ...
    }
}
```

---

# 5. Learning Module

POST /learning/path

Description

Generate learning roadmap.

Request

```json
{
    "resume_id":"resume_001",
    "job_id":"job_001"
}
```

Response

```json
{
    "success":true,
    "data":{
        ...
    }
}
```

---

# 6. Report Module

POST /report/generate

Description

Generate career report.

Request

```json
{
    "resume_id":"resume_001",
    "job_id":"job_001"
}
```

Response

```json
{
    "success":true,
    "report_url":"report/report001.pdf"
}
```

---

# Error Response

```json
{
    "success":false,
    "message":"Resume parsing failed."
}
```

Status Code

400 Bad Request

500 Internal Server Error