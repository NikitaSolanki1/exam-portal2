
<template>
    <Navbar />

    <div class="page">
        <div class="form-card">

            <h2>Create Rubric</h2>
            <p>Add evaluation criteria for this examination</p>

            <div v-if="message" class="message">
                {{ message }}
            </div>

            <form @submit.prevent="createRubric">

                <label>Criterion Name</label>
                <input
                    v-model="criterion_name"
                    type="text"
                    placeholder="Enter criterion name"
                    required
                >

                <label>Maximum Marks</label>
                <input
                    v-model="maximum_marks"
                    type="number"
                    min="0.1"
                    step="0.1"
                    placeholder="Enter maximum marks"
                    required
                >

                <button type="submit">Create Rubric</button>

                <button type="button" class="back-btn" @click="goBack">
                    Back
                </button>

            </form>
        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const criterion_name = ref('')
const maximum_marks = ref('')
const description = ref('')
const message = ref('')

const createRubric = async () => {
    try {
        const token = localStorage.getItem('access_token')

        const response = await axios.post(
            'http://127.0.0.1:5000/admin/create-rubric',
            {
                examination_id: route.params.id,
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

        if (response.data.message === 'Rubric created successfully') {
            criterion_name.value = ''
            maximum_marks.value = ''
            description.value = ''
        }

    } catch (error) {
        message.value = error.response?.data?.message ||
            'Unable to create rubric'
    }
}

const goBack = () => {
    router.push(`/manage-rubric/${route.params.id}`)
}
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.page {
    min-height: 100vh;
    background: #f5f7f5;
    padding: 35px 15px;
    font-family: Arial, sans-serif;
}

.form-card {
    max-width: 600px;
    margin: auto;
    background: white;
    padding: 30px;
    border: 1px solid #e5e5e5;
    border-radius: 7px;
}

h2 {
    color: #263b32;
    margin: 0 0 8px;
}

p {
    color: #777;
    margin-bottom: 25px;
}

label {
    display: block;
    color: #344b40;
    margin: 15px 0 7px;
    font-size: 14px;
}

input,
textarea {
    width: 100%;
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 4px;
    outline: none;
    font-family: Arial, sans-serif;
}

input:focus,
textarea:focus {
    border-color: #2f5d50;
}

textarea {
    min-height: 90px;
    resize: vertical;
}

button {
    width: 100%;
    padding: 11px;
    margin-top: 18px;
    background: #2f5d50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background: #24483d;
}

.back-btn {
    margin-top: 10px;
    background: #777;
}

.message {
    color: #2f5d50;
    margin-bottom: 12px;
}
</style>
