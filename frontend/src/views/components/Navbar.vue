<template>
  <nav>
    <div class="nav-brand"><router-link to="/" class="nav-brand">
        ExamPortal
      </router-link>
    </div>

    <div class="nav-links">
      <template v-if="loggedIn">

        <template v-if="role === 'Admin'">
          <router-link to="/admin/dashboard">Home</router-link>
          <router-link to="/admin/courses">Manage Course</router-link>
          <router-link to="/admin/examinations">Manage Examination</router-link>
          <router-link to="/admin/examiners">Manage Examiner</router-link>
          <router-link to="/admin/students">Manage Students</router-link>
          <router-link to="/admin/bookings">View Bookings

          </router-link>
        </template>

        <template v-else-if="role === 'Examiner'">
          <router-link to="/examiner/dashboard">Home</router-link>
          <router-link to="/examiner/examinations">Assigned Examination</router-link>
        </template>

        <template v-else-if="role === 'Student'">
          <router-link to="/student/dashboard">Home</router-link>
          <router-link to="/student/examination">Examinations</router-link>
          <router-link to="/student/bookings">My Bookings</router-link>
          <router-link to="/student/exam-history">Exam History</router-link>
          <router-link to="/student/results">See Results</router-link>
        </template>

        <button class="logout-btn" @click="logout">Logout</button>

      </template>

      <template v-else>
        <router-link to="/login">Login</router-link>
        <router-link to="/register">Signup</router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const loggedIn = ref(!!localStorage.getItem('role'))
const role = ref(localStorage.getItem('role') || '')

const logout = () => {
  localStorage.removeItem('role')
  localStorage.removeItem('name')
  localStorage.removeItem('user_id')

  loggedIn.value = false
  role.value = ''

  window.location.href = '/'
}
</script>

<style scoped>
nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 30px;
  background: #2f5d50;
  color: white;
}

.nav-brand {
  font-weight: bold;
  font-size: 21px;
  color: white;
  text-decoration: none;
  cursor: pointer;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 22px;
  flex-wrap: wrap;
}

a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

a:hover,
a.router-link-active {
  color: #c8e6c9;
}

.logout-btn {
  background: white;
  color: #2f5d50;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background: #e8f5e9;
}
</style>
