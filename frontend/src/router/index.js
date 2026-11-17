import { createRouter, createWebHistory } from 'vue-router'

import Index from '../views/Index.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import Admin from '../views/Admin.vue'
import Home from '../views/Admin.vue'
import Courses from '../views/Courses.vue'
import Examinations from '../views/Examinations.vue'
import Examiners from '../views/Examiners.vue'
import Students from '../views/Students.vue'
import CreateCourse from '../views/createcourse.vue'
import EditCourse from '../views/EditCourse.vue'
import CreateExamination from '../views/CreateExamination.vue'
import CreateExaminer from '../views/CreateExaminer.vue'
import ExaminerDashboard from '../views/ExaminerDashboard.vue'
import CreateRubric from '../views/CreateRubric.vue'
import ManageRubric from '../views/ManageRubric.vue'
import ViewSlot from '../views/ViewSlot.vue'
import ViewExamDetails from '../views/ViewExamDetails.vue'
import ViewBookings from '../views/ViewBookings.vue'
import AssignedExaminations from "../views/AssignedExaminations.vue"
import ManageSlots from "../views/ManageSlots.vue"
import ViewBookedStudents from "../views/ViewBookedStudents.vue"
import EvaluateStudents from "../views/EvaluateStudents.vue"
import ViewSubmittedEvaluations from "../views/ViewSubmittedEvaluations.vue"
import StudentDashboard from "../views/StudentDashboard.vue"
import StudentExamination from "../views/StudentExamination.vue"
import StudentExamDetails from '../views/StudentExamDetails.vue'
import StudentExamSlots from '../views/StudentExamSlots.vue'
import StudentMyBookings from '../views/StudentMyBookings.vue'
import ExaminerProfile from "../views/ExaminerProfile.vue"
import StudentExamHistory from '../views/StudentExamHistory.vue'
import StudentResults from '../views/StudentResults.vue'
import AdminEvaluations from '../views/AdminEvaluations.vue'
const routes = [
    {
        path: '/',
        name: 'Index',
        component: Index
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },

    {
        path: '/admin/dashboard',
        name: 'Admin',
        component: Admin

    },
    {
        path: '/admin/dashboard',
        component: Home
    },
    {
        path: '/admin/courses',
        component: Courses
    },
    {
        path: '/admin/examinations',
        component: Examinations
    },
    {
        path: '/admin/examiners',
        component: Examiners
    },
    {
        path: '/admin/students',
        component: Students
    },
    {
        path: '/admin/createcourse',
        component: CreateCourse
    },
    {
        path: '/admin/editcourse/:id',
        component: EditCourse
    },
    {
        path: '/admin/createexamination',
        component: CreateExamination
    },
    {
        path: '/admin/create-examiner',
        name: 'CreateExaminer',
        component: CreateExaminer
    },
    {
        path: '/examiner/dashboard',
        component: ExaminerDashboard
    },
    {
        path: '/create-rubric/:id',
        component: CreateRubric
    },
    {
        path: '/manage-rubric/:id',
        component: ManageRubric
    },
    {
        path: '/view_slot/:id',
        component: ViewSlot
    },
    {
        path: '/admin_exam_detail/:id',
        component: ViewExamDetails
    },
    {
        path: '/admin/bookings',
        component: ViewBookings
    },
    {
        path: "/examiner/examinations",
        component: AssignedExaminations
    },
    {
        path: "/examiner/slots",
        component: ManageSlots
    },
    {
        path: "/examiner/booked-students",
        component: ViewBookedStudents
    },
    {
        path: "/examiner/evaluations",
        component: EvaluateStudents
    },
    {
        path: "/examiner/submitted-evaluations",
        component: ViewSubmittedEvaluations
    },
    {
        path: "/student/dashboard",
        component: StudentDashboard
    },
    {
        path: "/student/examination",
        component: StudentExamination
    },
    {
        path: '/student/examination-details/:id',
        component: StudentExamDetails
    },
    {
        path: '/student/examination-slots/:id',
        component: StudentExamSlots
    },
    {
        path: '/student/bookings',
        component: StudentMyBookings
    },
    {
        path: "/examiner/profile",
        component: ExaminerProfile
    },
    {
        path: '/student/exam-history',
        name: 'StudentExamHistory',
        component: StudentExamHistory
    },
    {
        path: '/student/results',
        name: 'StudentResults',
        component: StudentResults
    },
    {   path: '/admin/evaluations',
        component: AdminEvaluations },



]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router