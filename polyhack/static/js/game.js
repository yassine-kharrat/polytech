const steps = [
  { title: "Step 1: Introduction", content: "Welcome to Step 1! Learn the basics of the game." },
  { title: "Step 2: Skills", content: "Step 2 covers the essential skills you'll need." },
  { title: "Step 3: Challenges", content: "Face your first challenges in Step 3!" },
  { title: "Step 4: Advanced Strategies", content: "Master advanced strategies to win the game." }
];

const courseContainer = document.getElementById('course');
const courseTitle = document.getElementById('course-title');
const courseContent = document.getElementById('course-content');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');

let currentStep = null;

// Show a course based on the step
function showCourse(index) {
  currentStep = index;
  courseTitle.textContent = steps[index].title;
  courseContent.textContent = steps[index].content;
  courseContainer.classList.add('active');

  // Disable buttons at boundaries
  prevBtn.disabled = index === 0;
  nextBtn.disabled = index === steps.length - 1;
}

// Hide the course container
function hideCourse() {
  courseContainer.classList.remove('active');
}

// Add event listeners to steps
document.querySelectorAll('.step').forEach((step, index) => {
  step.addEventListener('click', () => showCourse(index));
});

// Navigation button actions
prevBtn.addEventListener('click', () => {
  if (currentStep > 0) showCourse(currentStep - 1);
});

nextBtn.addEventListener('click', () => {
  if (currentStep < steps.length - 1) showCourse(currentStep + 1);
});
