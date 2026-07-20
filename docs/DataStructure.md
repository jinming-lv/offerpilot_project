# CareerPilot Data Structure

Version 1.0

---

# Resume JSON

```json
{
  "resume_id":"resume_001",

  "basic_info":{
      "name":"张三",
      "gender":"Male",
      "education":"Bachelor",
      "major":"Computer Science",
      "email":"example@gmail.com",
      "phone":"138xxxx"
  },

  "skills":[
      "Python",
      "Java",
      "MySQL",
      "Redis",
      "Docker",
      "Vue"
  ],

  "projects":[
      {
          "project_name":"Campus Trading Platform",
          "role":"Backend Developer",

          "description":"Responsible for backend development.",

          "tech_stack":[
              "Flask",
              "MySQL",
              "Vue"
          ]
      }
  ],

  "experience":[
      {
          "company":"ABC Company",
          "position":"Intern",
          "duration":"2025.07-2025.09"
      }
  ]
}
```

---

# Job JSON

```json
{
    "job_id":"job_001",

    "company":"ByteDance",

    "position":"Python Backend Engineer",

    "required_skills":[
        "Python",
        "MySQL",
        "Redis",
        "Docker",
        "Linux"
    ],

    "preferred_skills":[
        "Go",
        "Kubernetes"
    ],

    "education":"Bachelor",

    "experience":"1 year"
}
```

---

# Match JSON

```json
{
    "match_id":"match001",

    "resume_id":"resume001",

    "job_id":"job001",

    "score":88,

    "advantages":[
        "Python",
        "MySQL"
    ],

    "missing_skills":[
        "Docker",
        "Redis"
    ],

    "analysis":"The resume matches most of the job requirements."
}
```

---

# Interview JSON

```json
{
    "questions":[

        {
            "id":1,
            "category":"Python",

            "difficulty":"Easy",

            "question":"Explain GIL in Python."
        },

        {
            "id":2,
            "category":"Redis",

            "difficulty":"Medium",

            "question":"Why is Redis fast?"
        },

        {
            "id":3,
            "category":"Project",

            "difficulty":"Hard",

            "question":"Describe your biggest project."
        }
    ]
}
```

---

# Interview Result JSON

```json
{
    "overall_score":84,

    "details":[

        {
            "question_id":1,

            "score":90,

            "comment":"Good answer."
        },

        {
            "question_id":2,

            "score":75,

            "comment":"Need more details."
        }
    ]
}
```

---

# Learning Path JSON

```json
{
    "duration":"14 Days",

    "roadmap":[

        {
            "day":1,

            "topic":"Redis",

            "resource":"Redis Official Documentation"
        },

        {
            "day":2,

            "topic":"Docker",

            "resource":"Docker Tutorial"
        },

        {
            "day":3,

            "topic":"Linux",

            "resource":"Linux Command Guide"
        }
    ]
}
```

---

# Report JSON

```json
{
    "candidate":"张三",

    "target_job":"Python Backend Engineer",

    "match_score":88,

    "advantages":[
        "Python",
        "Project Experience"
    ],

    "weaknesses":[
        "Docker",
        "Redis"
    ],

    "learning_plan":"14 Days",

    "interview_score":84,

    "overall_evaluation":"Suitable for entry-level backend positions."
}
```

---

# Data Flow

```
Resume PDF

↓

Resume JSON

↓

Job JSON

↓

Match JSON

↓

Interview JSON

↓

Interview Result

↓

Learning Path

↓

Report
```
