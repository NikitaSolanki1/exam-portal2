<template>
    <Navbar />

    <div class="dashboard">

        <div class="welcome">
            <div>
                <h2>Welcome, {{ name }}</h2>
                <p>Manage your examinations and student evaluations</p>
            </div>

            <button @click="$router.push('/examiner/profile')">
                My Profile
            </button>
        </div>

        <div class="cards">

            <div class="card">
                <h3>{{ total_examinations }}</h3>
                <p>Assigned Examinations</p>
            </div>

            <div class="card">
                <h3>{{ total_slots }}</h3>
                <p>Created Slots</p>
            </div>

            <div class="card">
                <h3>{{ total_students }}</h3>
                <p>Booked Students</p>
            </div>

            <div class="card">
                <h3>{{ pending_evaluations }}</h3>
                <p>Pending Evaluations</p>
            </div>

        </div>

        <div class="section">

            <div class="section-heading">
                <div>
                    <h3>Assigned Examinations</h3>
                    <p>Examinations assigned to you by Admin</p>
                </div>
            </div>

            <div class="table-box">

                <table>
                    <thead>
                        <tr>
                            <th>Exam Name</th>
                            <th>Exam Type</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="exam in examinations" :key="exam.id">
                            <td>{{ exam.exam_name }}</td>
                            <td>{{ exam.exam_type }}</td>
                            <td>{{ exam.status }}</td>
                            <td>
                                <button class="view-btn" @click="$router.push('/examiner/examinations')">
                                    View
                                </button>
                            </td>
                        </tr>

                        <tr v-if="examinations.length === 0">
                            <td colspan="4" class="empty">
                                No examinations assigned yet.
                            </td>
                        </tr>
                    </tbody>
                </table>

            </div>

        </div>

        <div class="section">

            <h3>Quick Actions</h3>

            <div class="actions">
                <button @click="$router.push('/examiner/examinations')">
                    View Examinations
                </button>

                <button @click="$router.push('/examiner/slots')">
                    Manage Examination Slots
                </button>

                <button @click="$router.push('/examiner/booked-students')">
                    View Booked Students
                </button>

                <button @click="$router.push('/examiner/evaluations')">
                    Evaluate Students
                </button>
                <button @click="$router.push('/examiner/submitted-evaluations')">
                    View Submitted Evaluations
                </button>
            </div>

        </div>

        <p v-if="message" class="message">
            {{ message }}
        </p>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import Navbar from "./components/Navbar.vue"

const name = ref(localStorage.getItem("name") || "")

const total_examinations = ref(0)
const total_slots = ref(0)
const total_students = ref(0)
const pending_evaluations = ref(0)

const examinations = ref([])
const message = ref("")

const fetchDashboard = async () => {

    try {
        const response = await axios.get(
            "http://127.0.0.1:5000/examiner/dashboard",
            {
                headers: {
                    Authorization: "Bearer " + localStorage.getItem("access_token")
                }
            }
        )

        name.value = response.data.name

        total_examinations.value = response.data.total_examinations
        total_slots.value = response.data.total_slots
        total_students.value = response.data.total_students
        pending_evaluations.value = response.data.pending_evaluations

        examinations.value = response.data.examinations

    } catch (error) {
        message.value = error.response?.data?.message || "Unable to load dashboard"
    }
}

onMounted(() => {
    fetchDashboard()
})
</script>

<style scoped>
.dashboard {
    min-height: 100vh;
    background: #f5f8f6;
    padding: 30px;
}

.welcome {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.welcome h2 {
    color: #2f5d50;
    margin-bottom: 8px;
}

.welcome p {
    color: #777;
}

.welcome button,
.actions button {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 11px 18px;
    border-radius: 6px;
    cursor: pointer;
}

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 10px;
    border-left: 4px solid #2f5d50;
}

.card h3 {
    font-size: 28px;
    color: #2f5d50;
    margin-bottom: 10px;
}

.card p {
    color: #777;
}

.section {
    background: white;
    padding: 25px;
    border-radius: 10px;
    margin-bottom: 25px;
}

.section h3 {
    color: #2f5d50;
    margin-bottom: 8px;
}

.section-heading p {
    color: #777;
    margin-bottom: 20px;
}

.table-box {
    width: 100%;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px;
}

th,
td {
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background: #2f5d50;
    color: white;
}

.view-btn {
    background: #e2f0e9;
    color: #2f5d50;
    border: none;
    padding: 8px 14px;
    border-radius: 5px;
    cursor: pointer;
}

.empty {
    text-align: center;
    color: #777;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 18px;
}

.message {
    color: #2f5d50;
    margin-top: 15px;
}

</style>
