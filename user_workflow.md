2. Frontend workflow — what the user sees

Step 1. Authentication and role selection
Students sign up or log in. Educators get a separate dashboard with access to class-level insights.
Screens: Login, registration, role-based dashboard.




Step 2. Student dashboard
The student chooses a subject, views previous progress, and starts a diagnostic assessment or continues an existing learning path.
Screens: Subject selection, progress summary, start assessment.




Step 3. Adaptive quiz interface
Display one question at a time. Capture the selected answer, answer changes, time spent, attempts, and an optional confidence rating. Submit the interaction data to the backend.
The frontend displays the next question returned by the backend—it should not decide which question comes next.
Screens: Question, answer options, confidence selection, progress indicator.




Step 4. Knowledge and diagnosis report
After assessment, show the student's strengths, weak or uncertain concepts, suspected foundational gaps, and the evidence behind the diagnosis.
Visualize prerequisite relationships with different colors for mastered, uncertain, and weak concepts.
Screens: Concept graph, mastery summary, root-gap explanation.




Step 5. Personalized learning roadmap
Display an ordered list of concepts to learn. Each concept includes its reason for recommendation, lessons, practice questions, and resources at basic, intermediate, and advanced depths.
The student can choose how deeply to study, while prerequisite order is preserved.
Screens: Roadmap, lesson details, resource library, completion tracking.




Step 6. Retest and progress report
After studying a recommended concept, the student answers different questions. Display before-and-after mastery estimates, quiz performance, and unresolved gaps.
Screens: Retest, improvement report, updated roadmap.