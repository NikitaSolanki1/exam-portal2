
<template>
  <Navbar />

  <main class="index">

    <section class="hero">
      <p class="small-heading">EXAMINATION MANAGEMENT PORTAL</p>

      <h1>Welcome to Examination Portal</h1>

      <p class="description">
        Manage courses, examinations and examiner details from one place.
        This portal helps students and examiners access examination-related
        activities easily.
      </p>

      <div class="buttons">
        <a href="/login" class="login-btn">Login</a>
        <a href="/register" class="register-btn">Register</a>
      </div>
    </section>

    <section class="details">
      <h2>Portal Features</h2>
      <p class="section-text">
        Everything related to examinations in one place.
      </p>

      <div class="cards">

        <article>
          <h3>Courses</h3>
          <p>
            View and manage courses with course code, name,
            department and other details.
          </p>
        </article>

        <article>
          <h3>Examinations</h3>
          <p>
            Schedule examinations, manage exam dates
            and check examination details.
          </p>
        </article>

        <article>
          <h3>Examiners</h3>
          <p>
            Manage examiner accounts and assign examiners
            to different examinations.
          </p>
        </article>

        <article>
          <h3>Exam Booking</h3>
          <p>
            Students can view available examination slots
            and book their preferred slots.
          </p>
        </article>

      </div>
    </section>

    <section class="roles">
      <h2>Who Can Use This Portal?</h2>

      <div class="role-list">
        <div>
          <h3>Admin</h3>
          <p>Manage courses, examinations, students and examiners.</p>
        </div>

        <div>
          <h3>Examiner</h3>
          <p>Manage assigned examinations and evaluate students.</p>
        </div>

        <div>
          <h3>Student</h3>
          <p>View examinations and book available examination slots.</p>
        </div>
      </div>
    </section>

    <footer>
      <p>Examination Management Portal</p>
    </footer>

  </main>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>

<style scoped>
.home {
  max-width: 1100px;
  margin: auto;
  padding: 25px 20px;
  font-family: Arial, sans-serif;
  color: #303943;
}

.hero {
  background: #2f5d50;
  color: white;
  padding: 45px 40px;
  border-radius: 6px;
}

.small-heading {
  font-size: 12px;
  letter-spacing: 1px;
  color: #d5e7dc;
  margin-bottom: 12px;
}

.hero h1 {
  font-size: 32px;
  margin: 0 0 15px;
}

.description {
  max-width: 650px;
  font-size: 15px;
  line-height: 1.7;
  color: #edf4ef;
}

.buttons {
  display: flex;
  gap: 12px;
  margin-top: 25px;
}

.buttons a {
  text-decoration: none;
  padding: 11px 22px;
  border-radius: 4px;
  font-size: 14px;
}

.login-btn {
  background: white;
  color: #2f5d50;
}

.register-btn {
  border: 1px solid white;
  color: white;
}

.buttons a:hover {
  opacity: 0.85;
}


.details {
  margin-top: 40px;
}

.details h2,
.roles h2 {
  font-size: 23px;
  margin-bottom: 8px;
}

.section-text {
  color: #7c8580;
  font-size: 14px;
  margin-bottom: 20px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}

article {
  background: white;
  border: 1px solid #e1e7e3;
  padding: 22px;
  border-radius: 5px;
}

article h3 {
  margin: 0 0 10px;
  color: #2f5d50;
  font-size: 18px;
}

article p {
  color: #737c76;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.roles {
  margin-top: 40px;
}

.role-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 20px;
}

.role-list div {
  background: #f5f8f6;
  padding: 18px;
  border-left: 3px solid #2f5d50;
}

.role-list h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.role-list p {
  color: #737c76;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}


footer {
  margin-top: 45px;
  padding: 18px;
  border-top: 1px solid #e5e9e6;
  text-align: center;
  color: #858d88;
  font-size: 13px;
}

@media (max-width: 650px) {
  .hero {
    padding: 30px 22px;
  }

  .hero h1 {
    font-size: 25px;
  }

  .cards {
    grid-template-columns: 1fr;
  }

  .role-list {
    grid-template-columns: 1fr;
  }
}
</style>
