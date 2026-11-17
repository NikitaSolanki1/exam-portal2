
<template>
  <Navbar />

  <div class="admin-page">
    <div class="dashboard">
      <h2>Welcome Admin</h2>
      <p>Welcome to Examination Management Portal.</p>

      <div class="stats-section">
        <h3>Dashboard Overview</h3>

        <div class="stats">
          <div class="stat-card">
            <h3>Total Courses</h3>
            <h2>{{ dashboard.total_courses }}</h2>
          </div>

          <div class="stat-card">
            <h3>Total Examinations</h3>
            <h2>{{ dashboard.total_examinations }}</h2>
          </div>

          <div class="stat-card">
            <h3>Total Examiners</h3>
            <h2>{{ dashboard.total_examiners }}</h2>
          </div>

          <div class="stat-card">
            <h3>Total Students</h3>
            <h2>{{ dashboard.total_students }}</h2>
          </div>

          <div class="stat-card">
            <h3>Examination Slots</h3>
            <h2>{{ dashboard.total_slots }}</h2>
          </div>

          <div class="stat-card">
            <h3>Total Bookings</h3>
            <h2>{{ dashboard.total_bookings }}</h2>
          </div>
        </div>
      </div>

      <div class="overview">
        <div class="card">
          <h3>Courses</h3>
          <p>Manage courses</p>
          <button @click="router.push('/admin/courses')">
            View Courses
          </button>
        </div>

        <div class="card">
          <h3>Examiners</h3>
          <p>Manage examiners</p>
          <button @click="router.push('/admin/examiners')">
            View Examiners
          </button>
        </div>

        <div class="card">
          <h3>Evaluations</h3>
          <p>Review submitted evaluations and publish results</p>
          <button @click="router.push('/admin/evaluations')">
            View Evaluations
          </button>
        </div>
      </div>

      <h3 class="heading">Quick Actions</h3>

      <div class="actions">
        <button @click="router.push('/admin/createexamination')">
          Create Examination
        </button>

        <button @click="router.push('/admin/createcourse')">
          Create Course
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const router = useRouter()

const dashboard = ref({
  total_courses: 0,
  total_examinations: 0,
  total_examiners: 0,
  total_students: 0,
  total_slots: 0,
  total_bookings: 0
})

const getDashboard = async () => {
  try {
    const token = localStorage.getItem("access_token")

    const response = await axios.get(
      'http://127.0.0.1:5000/admin/dashboard',
      {
        headers: {
          Authorization: 'Bearer ' + token
        }
      }
    )

    dashboard.value = response.data

  } catch (error) {
    console.log(error.response?.data || error.message)
  }
}

onMounted(() => {
  getDashboard()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard {
  max-width: 1000px;
  margin: 35px auto;
  padding: 0 20px;
}

.dashboard h2 {
  color: #333;
}

.dashboard p {
  color: #666;
}

.stats-section {
  margin-top: 30px;
}

.stats-section h3 {
  color: #333;
  margin-bottom: 18px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.stat-card {
  background: white;
  border: 1px solid #ddd;
  padding: 20px;
}

.stat-card h3 {
  color: #555;
  font-size: 16px;
  margin: 0;
}

.stat-card h2 {
  color: #2f5d50;
  font-size: 28px;
  margin: 15px 0 0;
}

.overview {
  display: flex;
  gap: 20px;
  margin-top: 25px;
}

.card {
  background: white;
  border: 1px solid #ddd;
  padding: 22px;
  width: 33.33%;
}

.card h3 {
  color: #2f5d50;
}

.card button,
.actions button {
  background: #2f5d50;
  color: white;
  border: none;
  padding: 10px 18px;
  cursor: pointer;
}

.card button:hover,
.actions button:hover {
  background: #24483e;
}

.heading {
  margin-top: 35px;
  color: #333;
}

.actions {
  display: flex;
  gap: 15px;
}
</style>
