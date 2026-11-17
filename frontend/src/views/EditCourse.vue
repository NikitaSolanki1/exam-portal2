<template>
  <div class="content">

    <div class="page-heading">
      <div>
        <h2>Edit Course</h2>
        <p>Update course details</p>
      </div>

      <button class="back-btn" @click="router.push('/admin/courses')">
        Back to Courses
      </button>
    </div>

    <div class="form-box">

      <form @submit.prevent="updateCourse">

        <div class="form-grid">

          <div class="form-group">
            <label>Course Code</label>
            <input v-model="form.course_code" type="text" required>
          </div>

          <div class="form-group">
            <label>Course Name</label>
            <input v-model="form.course_name" type="text" required>
          </div>

          <div class="form-group">
            <label>Department</label>
            <input v-model="form.department" type="text" required>
          </div>

          <div class="form-group">
            <label>Credit</label>
            <input v-model.number="form.credit" type="number" min="1" required>
          </div>

          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status">
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" required></textarea>
          </div>

        </div>

        <p>{{ message }}</p>

        <div class="form-actions">
          <button type="submit" class="save-btn">Save Changes</button>

          <button type="button" class="cancel-btn"
            @click="router.push('/admin/courses')">
            Cancel
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const message = ref('')

const form = ref({
  course_code: '',
  course_name: '',
  department: '',
  credit: '',
  description: '',
  status: 'Active'
})

const token = localStorage.getItem('access_token')

const getCourse = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/editcourse/${route.params.id}`,
      {
        headers: {
          Authorization: 'Bearer ' + token
        }
      }
    )

    form.value = response.data

  } catch (error) {
    message.value = error.response?.data?.message || 'Unable to connect to server'
  }
}

const updateCourse = async () => {
  try {
    const response = await axios.post(
      `http://127.0.0.1:5000/editcourse/${route.params.id}`,
      {
        course_code: form.value.course_code,
        course_name: form.value.course_name,
        department: form.value.department,
        credit: form.value.credit,
        description: form.value.description,
        status: form.value.status
      },
      {
        headers: {
          Authorization: 'Bearer ' + token
        }
      }
    )

    message.value = response.data.message
    router.push('/admin/courses')

  } catch (error) {
    message.value = error.response?.data?.message || 'Unable to connect to server'
  }
}

onMounted(() => {
  getCourse()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.content {
  min-height: 100vh;
  padding: 30px 35px;
  background: #f5f7f5;
  font-family: Arial, sans-serif;
}

.page-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.page-heading h2 {
  margin: 0 0 7px;
  color: #263b32;
}

.page-heading p {
  margin: 0;
  color: #777;
}

.back-btn {
  background: white;
  color: #2f5d50;
  border: 1px solid #2f5d50;
  padding: 10px 18px;
  border-radius: 4px;
  cursor: pointer;
}

.form-box {
  background: white;
  padding: 25px;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  max-width: 900px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #344b40;
  font-weight: 600;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 11px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 100%;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 22px;
}

.save-btn {
  background: #2f5d50;
  color: white;
  border: none;
  padding: 11px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background: #eee;
  color: #444;
  border: none;
  padding: 11px 20px;
  border-radius: 4px;
  cursor: pointer;
}

@media (max-width: 700px) {
  .content {
    padding: 20px 15px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>