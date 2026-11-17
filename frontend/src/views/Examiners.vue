
<template>
    <Navbar />

    <div class="content">

        <div class="page-heading">
            <h1>Manage Examiner</h1>

            <button class="create-btn" @click="router.push('/admin/create-examiner')">
                Create Examiner
            </button>
        </div>

        <p v-if="message" class="message">{{ message }}</p>

        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Blocked</th>
                    <th>Action</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="examiner in examiners" :key="examiner.id">
                    <td>{{ examiner.name }}</td>
                    <td>{{ examiner.email }}</td>
                    <td>{{ examiner.role }}</td>
                    <td>{{ examiner.is_blocked ? 'Yes' : 'No' }}</td>

                    <td>
                        <button
                            class="action-btn"
                            @click="blockExaminer(examiner.id)"
                            :disabled="examiner.is_blocked"
                        >
                            Block
                        </button>

                        <button
                            class="action-btn"
                            @click="unblockExaminer(examiner.id)"
                            :disabled="!examiner.is_blocked"
                        >
                            Unblock
                        </button>
                    </td>
                </tr>

                <tr v-if="examiners.length === 0">
                    <td colspan="5">No Examiners Found</td>
                </tr>
            </tbody>
        </table>

    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const examiners = ref([])
const message = ref('')

const fetchExaminerDetails = async () => {
    try {
        const token = localStorage.getItem('access_token')

        if (!token) {
            message.value = "Please login again"
            return
        }

        const response = await axios.get(
            "http://127.0.0.1:5000/provide_examinor_details",
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        examiners.value = response.data.data

    } catch (error) {
        console.log(error.response?.data || error.message)
        message.value = error.response?.data?.msg ||
                        error.response?.data?.message ||
                        "Unable to load examiners"
    }
}

const blockExaminer = async (id) => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            `http://127.0.0.1:5000/block_examinor/${id}`,
            {},
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message
        await fetchExaminerDetails()

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

const unblockExaminer = async (id) => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            `http://127.0.0.1:5000/unblock_examinor/${id}`,
            {},
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message
        await fetchExaminerDetails()

    } catch (error) {
        console.log(error.response?.data || error.message)
    }
}

onMounted(() => {
    fetchExaminerDetails()
})
</script>

<style scoped>
.content {
    max-width: 1000px;
    margin: 35px auto;
    padding: 20px;
}

.page-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

h1 {
    color: #2f5d50;
    margin: 0;
}

.create-btn {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 10px 18px;
    cursor: pointer;
}

.create-btn:hover,
.action-btn:hover {
    background: #24483e;
}

.message {
    color: #2f5d50;
    margin-bottom: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

th {
    background: #2f5d50;
    color: white;
}

.action-btn {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 8px 12px;
    margin: 3px;
    cursor: pointer;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>
