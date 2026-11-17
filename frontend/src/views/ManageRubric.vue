
<template>
    <Navbar />

    <div class="page">
        <div class="content">

            <div class="page-heading">
                <div>
                    <h2>Manage Rubric</h2>
                    <p>View, edit and delete examination rubrics</p>
                </div>

                <button class="create-btn" @click="router.push(`/create-rubric/${route.params.id}`)">
                    Create Rubric
                </button>
            </div>

            <div class="table-box">

                <table>
                    <thead>
                        <tr>
                            <th>Criterion Name</th>
                            <th>Maximum Marks</th>
                            <th>Description</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="rubric in rubrics" :key="rubric.id">
                            <td>{{ rubric.criterion_name }}</td>
                            <td>{{ rubric.maximum_marks }}</td>
                            <td>{{ rubric.description }}</td>

                            <td>
                                <button class="edit-btn" @click="editRubric(rubric)">
                                    Edit
                                </button>

                                <button class="delete-btn" @click="deleteRubric(rubric.id)">
                                    Delete
                                </button>
                            </td>
                        </tr>

                        <tr v-if="rubrics.length === 0">
                            <td colspan="4" class="no-data">
                                No rubrics found
                            </td>
                        </tr>
                    </tbody>
                </table>

            </div>

            <div v-if="editing" class="edit-box">

                <h3>Edit Rubric</h3>

                <label>Criterion Name</label>
                <input v-model="criterion_name" type="text">

                <label>Maximum Marks</label>
                <input v-model="maximum_marks" type="number" min="0.1" step="0.1">

                <label>Description</label>
                <textarea v-model="description"></textarea>

                <button class="save-btn" @click="updateRubric">
                    Update Rubric
                </button>

                <button class="cancel-btn" @click="editing = false">
                    Cancel
                </button>

            </div>

            <p class="message">{{ message }}</p>

            <button class="back-btn" @click="router.push('/admin/examinations')">
                Back to Examinations
            </button>

        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const rubrics = ref([])
const message = ref('')
const editing = ref(false)

const rubric_id = ref('')
const criterion_name = ref('')
const maximum_marks = ref('')
const description = ref('')

const fetchRubrics = async () => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.get(
            `http://127.0.0.1:5000/admin/rubrics/${route.params.id}`,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        rubrics.value = response.data

    } catch (error) {
        console.log(error.response?.data || error.message)
        message.value = error.response?.data?.message ||
            'Unable to load rubrics'
    }
}

const editRubric = (rubric) => {
    rubric_id.value = rubric.id
    criterion_name.value = rubric.criterion_name
    maximum_marks.value = rubric.maximum_marks
    description.value = rubric.description

    editing.value = true
}

const updateRubric = async () => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.put(
            `http://127.0.0.1:5000/admin/edit-rubric/${rubric_id.value}`,
            {
                criterion_name: criterion_name.value,
                maximum_marks: maximum_marks.value,
                description: description.value
            },
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message

        if (response.data.message === 'Rubric updated successfully') {
            editing.value = false
            await fetchRubrics()
        }

    } catch (error) {
        message.value = error.response?.data?.message ||
            'Unable to update rubric'
    }
}

const deleteRubric = async (id) => {

    if (!confirm('Are you sure you want to delete this rubric?')) {
        return
    }

    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.delete(
            `http://127.0.0.1:5000/admin/delete-rubric/${id}`,
            {
                headers: {
                    Authorization: 'Bearer ' + token
                }
            }
        )

        message.value = response.data.message

        if (response.data.message === 'Rubric deleted successfully') {
            await fetchRubrics()
        }

    } catch (error) {
        message.value = error.response?.data?.message ||
            'Unable to delete rubric'
    }
}

onMounted(() => {
    fetchRubrics()
})
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.page {
    min-height: 100vh;
    background: #f5f7f5;
    font-family: Arial, sans-serif;
}

.content {
    padding: 30px 35px;
}

.page-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.page-heading h2 {
    color: #263b32;
    margin: 0 0 7px;
}

.page-heading p {
    color: #777;
    margin: 0;
}

.table-box,
.edit-box {
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 20px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    background: #edf2ef;
    color: #344b40;
    text-align: left;
    padding: 13px;
    font-size: 14px;
}

td {
    padding: 13px;
    border-bottom: 1px solid #eee;
    color: #555;
    font-size: 14px;
}

.create-btn,
.edit-btn,
.delete-btn,
.save-btn,
.cancel-btn,
.back-btn {
    border: none;
    padding: 9px 13px;
    border-radius: 4px;
    color: white;
    cursor: pointer;
    margin: 3px;
}

.create-btn,
.edit-btn,
.save-btn {
    background: #2f5d50;
}

.delete-btn {
    background: #777;
}

.cancel-btn {
    background: #888;
}

.back-btn {
    background: #2f5d50;
    margin-top: 15px;
}

.create-btn:hover,
.edit-btn:hover,
.save-btn:hover,
.back-btn:hover {
    background: #24483d;
}

.edit-box {
    max-width: 600px;
}

.edit-box h3 {
    color: #263b32;
}

.edit-box label {
    display: block;
    margin: 13px 0 7px;
    color: #344b40;
}

.edit-box input,
.edit-box textarea {
    width: 100%;
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 4px;
    outline: none;
}

.edit-box textarea {
    min-height: 80px;
    resize: vertical;
}

.no-data {
    text-align: center;
    padding: 25px;
    color: #888;
}

.message {
    color: #2f5d50;
    text-align: center;
    margin-top: 15px;
}
</style>
