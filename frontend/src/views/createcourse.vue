<template>
    <Navbar/>
    <div class="content">
        <div class="page-heading">
            <div>
                <h2>Create Course</h2>
                <p>Add a new course to the portal</p>
            </div>

            <button class="back-btn" @click="router.push('/admin/courses')">
                Back to Courses
            </button>
        </div>

        <div class="form-box">
            <form @submit.prevent="createCourse">

                <div class="form-grid">
                    <div class="form-group">
                        <label>Course Code</label>
                        <input v-model="courseCode" type="text" placeholder="Enter course code" required>
                    </div>

                    <div class="form-group">
                        <label>Course Name</label>
                        <input v-model="courseName" type="text" placeholder="Enter course name" required>
                    </div>

                    <div class="form-group">
                        <label>Department</label>
                        <input v-model="department" type="text" placeholder="Enter department" required>
                    </div>

                    <div class="form-group">
                        <label>Credit</label>
                        <input v-model.number="credit" type="number" placeholder="Enter credit" min="1" required>
                    </div>

                    <div class="form-group">
                        <label>Status</label>
                        <select v-model="status">
                            <option value="Active">Active</option>
                            <option value="Inactive">Inactive</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Description</label>
                        <textarea v-model="description" placeholder="Enter course description" required></textarea>
                    </div>
                </div>

                <p>{{ message }}</p>

                <div class="form-actions">
                    <button type="submit" class="create-btn">Create Course</button>
                    <button type="button" class="cancel-btn" @click="router.push('/admin/courses')">
                        Cancel
                    </button>
                </div>

            </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Navbar from './components/Navbar.vue'

const router = useRouter()

const courseCode = ref('')
const courseName = ref('')
const department = ref('')
const description = ref('')
const credit = ref('')
const status = ref('Active')
const message = ref('')

const createCourse = async () => {
    try {
        const response = await axios.post(
            'http://127.0.0.1:5000/createcourse',
            {
                course_code: courseCode.value,
                course_name: courseName.value,
                department: department.value,
                description: description.value,
                credit: credit.value,
                status: status.value
            },
            {
                headers: {
                    Authorization: 'Bearer ' + localStorage.getItem('access_token')
                }
            }
        )

        message.value = response.data.message

        courseCode.value = ''
        courseName.value = ''
        department.value = ''
        description.value = ''
        credit.value = ''
        status.value = 'Active'

        router.push('/admin/courses')

    } catch (error) {
        message.value = error.response?.data?.message || 'Unable to create course'
    }
}


</script>

<style scoped>
.create-page {
    min-height: 100vh;
    background: #f5f7f5;
    font-family: Arial, sans-serif;
}

.navbar {
    background: #2f5d50;
    color: white;
    padding: 15px 35px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar h2 {
    margin: 0;
}

.navbar button {
    margin-left: 20px;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.content {
    padding: 30px 35px;
}

.content p {
    color: #777;
}

.form-box {
    background: white;
    padding: 25px;
    max-width: 700px;
    border: 1px solid #e5e5e5;
    border-radius: 5px;
    margin-top: 25px;
}

form {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

form input,
form textarea,
form select {
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 10px;
    font-size: 14px;
}

form textarea {
    min-height: 90px;
    resize: vertical;
}

.actions {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}

.actions button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 11px 20px;
    border-radius: 4px;
    cursor: pointer;
}

.actions .cancel {
    background: #777;
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

.create-btn {
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


.page-heading {
    align-items: flex-start;
    gap: 15px;
    flex-direction: column;
}
</style>