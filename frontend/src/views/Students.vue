<template>
    <Navbar />

    <div class="student-page">

        <div class="heading">
            <div>
                <h2>Manage Students</h2>
                <p>View and manage registered students.</p>
            </div>

            <button class="back-btn" @click="router.push('/admin/dashboard')">
                Back to Dashboard
            </button>
        </div>

        <div class="search-box">
            <input type="text" v-model="search" @input="getStudents" placeholder="Search by Student Name, ID or Email">
        </div>

        <p class="message" v-if="message">{{ message }}</p>

        <div class="table-box">
            <table>
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="student in students" :key="student.id">
                        <td>{{ student.id }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.email }}</td>

                        <td>
                            <span :class="student.is_blocked ? 'blocked' : 'active'">
                                {{ student.is_blocked ? 'Blocked' : 'Active' }}
                            </span>
                        </td>

                        <td class="actions">
                            <button @click="viewDetails(student)">
                                View Details
                            </button>

                            <button v-if="!student.is_blocked" class="block-btn"
                                @click="changeStatus(student.id, 'block')">
                                Block
                            </button>

                            <button v-else class="unblock-btn" @click="changeStatus(student.id, 'unblock')">
                                Unblock
                            </button>
                        </td>
                    </tr>

                    <tr v-if="students.length === 0">
                        <td colspan="5" class="empty">
                            No Students Found
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="table-box details" v-if="selectedStudent">
            <div class="details-heading">
                <h3>Student Details</h3>
                <button @click="selectedStudent = null">Close</button>
            </div>

            <p><strong>Student ID:</strong> {{ selectedStudent.id }}</p>
            <p><strong>Name:</strong> {{ selectedStudent.name }}</p>
            <p><strong>Email:</strong> {{ selectedStudent.email }}</p>
            <p><strong>Phone:</strong> {{ selectedStudent.phone || 'Not provided' }}</p>
            <p><strong>Address:</strong> {{ selectedStudent.address || 'Not provided' }}</p>
            <p><strong>Past Experience:</strong> {{ selectedStudent.past_experience || 'Not provided' }}</p>
            <p>
                <strong>Status:</strong>
                {{ selectedStudent.is_blocked ? 'Blocked' : 'Active' }}
            </p>
        </div>

    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const students = ref([])
const selectedStudent = ref(null)
const search = ref("")
const message = ref("")

const getStudents = async () => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.get(
            'http://127.0.0.1:5000/admin/students',
            {
                params: {
                    search: search.value
                },
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        students.value = response.data.data || []

        if (selectedStudent.value) {
            const updatedStudent = students.value.find(
                student => student.id === selectedStudent.value.id
            )

            selectedStudent.value = updatedStudent || null
        }

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to get students"
    }
}

const viewDetails = (student) => {
    selectedStudent.value = student
}

const changeStatus = async (studentId, action) => {
    try {
        const token = localStorage.getItem("access_token")

        const response = await axios.post(
            'http://127.0.0.1:5000/admin/student/' + studentId + '/' + action,
            {},
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message
        await getStudents()

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to update student"
    }
}

onMounted(() => {
    getStudents()
})
</script>

<style scoped>
.student-page {
    min-height: 100vh;
    background: #f5f5f5;
    padding: 30px;
}

.heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.heading h2 {
    color: #333;
}

.heading p {
    color: #666;
}

.search-box {
    margin: 25px 0;
}

.search-box input {
    width: 350px;
    padding: 11px;
    border: 1px solid #ddd;
    background: white;
}

.table-box {
    background: white;
    border: 1px solid #ddd;
    padding: 15px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 13px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background: #2f5d50;
    color: white;
}

.active {
    color: green;
    font-weight: bold;
}

.blocked {
    color: #c0392b;
    font-weight: bold;
}

.actions {
    display: flex;
    gap: 8px;
}

button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 8px 11px;
    cursor: pointer;
}

button:hover {
    background: #24483e;
}

.block-btn {
    background: #c0392b;
}

.unblock-btn {
    background: #2f5d50;
}

.back-btn {
    padding: 10px 15px;
}

.empty {
    text-align: center;
    color: #666;
}

.details {
    margin-top: 30px;
}

.details h3 {
    color: #2f5d50;
}

.details p {
    color: #444;
    margin: 12px 0;
}

.details-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.message {
    color: #2f5d50;
    margin: 15px 0;
}
</style>
