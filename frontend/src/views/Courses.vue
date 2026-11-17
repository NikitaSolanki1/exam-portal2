<template>
    <Navbar />
    <div class="course-page">
       

        
        <div class="content">
            <div class="page-heading">
                <div>
                    <h2>Courses</h2>
                    <p>Manage all available courses</p>
                </div>
                <button class="add-btn" @click="router.push('/admin/createcourse')">
                    Add Course
                </button>
            </div>

            <div class="table-box">
                <div class="table-heading">
                    <h3>Course List</h3>
                    <input v-model="search" type="text" placeholder="Search course..." class="search">
                </div>

                <p v-if="message" class="message">{{ message }}</p>

                <div class="table-scroll">
                    <table>
                        <thead>
                            <tr>
                                <th>Course Code</th>
                                <th>Course Name</th>
                                <th>Department</th>
                                <th>Description</th>
                                <th>Credit</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="course in filteredCourses" :key="course.id">
                                <td>{{ course.course_code }}</td>
                                <td>{{ course.course_name }}</td>
                                <td>{{ course.department }}</td>
                                <td>{{ course.description }}</td>
                                <td>{{ course.credit }}</td>
                                <td>
                                    <span :class="course.status === 'Active' ? 'active-status' : 'inactive-status'">
                                        {{ course.status }}
                                    </span>
                                </td>
                                <td>
                                    <button class="edit-btn" @click="router.push('/admin/editcourse/' + course.id)">
                                        Edit
                                    </button>
                                    <button class="delete-btn" @click="deleteCourse(course.id)">Delete</button>
                                </td>
                            </tr>

                            <tr v-if="filteredCourses.length === 0">
                                <td colspan="7" class="no-data">No courses found</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const courses = ref([])
const search = ref('')
const message = ref('')
const editingCourse = ref(null)

const form = ref({
    course_code: '',
    course_name: '',
    department: '',
    description: '',
    credit: '',
    status: 'Active'
})

const token = () => localStorage.getItem('access_token')

const filteredCourses = computed(() => {
    return courses.value.filter(course => {
        const value = search.value.toLowerCase()

        return (
            course.course_code?.toLowerCase().includes(value) ||
            course.course_name?.toLowerCase().includes(value) ||
            course.department?.toLowerCase().includes(value)
        )
    })
})

const getCourses = async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/courses', {
            headers: {
                Authorization: 'Bearer ' + token()
            }
        })

        const data = await response.json()

        if (response.ok) {
            courses.value = data
        } else {
            message.value = data.message || 'Unable to load courses'
        }
    } catch (error) {
        message.value = 'Unable to connect to server'
    }
}

const saveCourse = async () => {
    try {
        const isEditing = !!editingCourse.value

        const url = isEditing
            ? `http://127.0.0.1:5000/courses/${editingCourse.value.id}`
            : 'http://127.0.0.1:5000/courses'

        const response = await fetch(url, {
            method: isEditing ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: 'Bearer ' + token()
            },
            body: JSON.stringify(form.value)
        })

        const data = await response.json()

        if (response.ok) {
            message.value = data.message || 'Course saved successfully'
            cancelForm()
            getCourses()
        } else {
            message.value = data.message || 'Unable to save course'
        }
    } catch (error) {
        message.value = 'Unable to connect to server'
    }
}

const editCourse = (course) => {
    editingCourse.value = course
    showAddForm.value = false

    form.value = {
        course_code: course.course_code,
        course_name: course.course_name,
        department: course.department,
        description: course.description,
        credit: course.credit,
        status: course.status
    }
}

const deleteCourse = async (id) => {

    try {
        await fetch(`http://127.0.0.1:5000/courses/${id}`, {
            method: 'DELETE',
            headers: {
                Authorization: 'Bearer ' + token()
            }
        })

        getCourses()

    } catch (error) {
        console.log(error)
    }
}

const cancelForm = () => {
    showAddForm.value = false
    editingCourse.value = null

    form.value = {
        course_code: '',
        course_name: '',
        department: '',
        description: '',
        credit: '',
        status: 'Active'
    }
}



onMounted(() => {
    getCourses()
})
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.course-page {
    min-height: 100vh;
    background: #f5f7f5;
    font-family: Arial, sans-serif;
}

.navbar {
    height: 65px;
    background: #2f5d50;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 35px;
}

.nav-title {
    font-size: 22px;
    font-weight: 600;
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 22px;
}

.nav-right button {
    background: white;
    color: #2f5d50;
    border: none;
    padding: 9px 18px;
    border-radius: 4px;
    cursor: pointer;
}

.menu {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    width: 100%;
}

.menu button {
    border: none;
    background: transparent;
    padding: 10px 16px;
    color: #444;
    cursor: pointer;
}

.menu button.active {
    background: #e5f0e9;
    color: #2f5d50;
    border-radius: 4px;
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
    margin: 0 0 7px;
    color: #263b32;
}

.page-heading p {
    margin: 0;
    color: #777;
}

.add-btn,
.save-btn {
    background: #2f5d50;
    color: white;
    border: none;
    padding: 11px 20px;
    border-radius: 4px;
    cursor: pointer;
}

.form-box,
.table-box {
    background: white;
    padding: 22px;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    margin-bottom: 25px;
}

.form-box h3,
.table-heading h3 {
    margin-top: 0;
    color: #263b32;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
}

.form-grid input,
.form-grid select,
.search {
    padding: 11px;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 100%;
}

.form-actions {
    display: flex;
    gap: 10px;
    margin-top: 18px;
}

.cancel-btn {
    background: #eee;
    border: none;
    padding: 10px 18px;
    border-radius: 4px;
    cursor: pointer;
}

.table-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
}

.table-heading h3 {
    margin-bottom: 0;
}

.search {
    max-width: 280px;
}

.table-scroll {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 850px;
}

th,
td {
    text-align: left;
    padding: 14px 12px;
    border-bottom: 1px solid #e8e8e8;
    font-size: 14px;
}

th {
    background: #f1f5f2;
    color: #344b40;
    font-weight: 600;
}

.edit-btn,
.delete-btn {
    padding: 7px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-right: 6px;
}

.edit-btn {
    background: #e6efe9;
    color: #2f5d50;
}

.delete-btn {
    background: #f7e8e8;
    color: #a33a3a;
}

.active-status {
    color: #267044;
}

.inactive-status {
    color: #a33a3a;
}

.no-data {
    text-align: center;
    color: #777;
    padding: 25px;
}

.message {
    color: #2f5d50;
}

@media (max-width: 700px) {

    .navbar,
    .menu {
        padding-left: 15px;
        padding-right: 15px;
    }

    .menu {
        overflow-x: auto;
    }

    .content {
        padding: 20px 15px;
    }

    .form-grid {
        grid-template-columns: 1fr;
    }

    .table-heading {
        align-items: flex-start;
        flex-direction: column;
    }
}
</style>
