import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from './pages/Login'

import WithdrawGame from '@/pages/library/WithdrawGame'
import AddGame from '@/pages/library/AddGame'
import LibraryDashboard from '@/pages/library/Dashboard'
import Configurations from "@/pages/admin/Configurations"

import authorizationService from '@/services/authorization.service'
import PageNotFound from '@/pages/PageNotFound'
import LibraryHome from "@/pages/library/home/LibraryHome"
import Dashboard from "@/pages/dashboard/home"
import StoreHome from "@/pages/store/home/StoreHome"
import StoreAddGame from "@/pages/store/new/NewGame"
import GoogleDocs from "@/pages/google-docs/GoogleDocs"

Vue.use(VueRouter)

//Guardians
function guardAuthenticated(to, from, next) {
  if (authorizationService.isAuthenticated()) {
    next()
  } else {
    next({ name: 'Login' })
  }
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: LibraryHome,
    props: { title: 'Library', pretitle: 'leiriacon 2022' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    props: { title: 'Dashboard', pretitle: 'leiriacon 2022' },
  },
  {
    path: '/library',
    name: 'LibraryHome',
    component: LibraryHome,
    props: { title: 'Library', pretitle: 'leiriacon 2022' },
  },
  {
    path: '/library/dashboard',
    name: 'LibraryDashboard',
    beforeEnter: guardAuthenticated,
    component: LibraryDashboard,
  },
  {
    path: '/library/:id/withdraw',
    name: 'WithdrawGame',
    props: { title: 'Withdraw game', pretitle: 'Library' },
    beforeEnter: guardAuthenticated,
    component: WithdrawGame,
  },

  {
    path: '/library/new',
    name: 'AddLibraryGame',
    beforeEnter: guardAuthenticated,
    component: AddGame,
  },
  {
    path: '/store',
    name: 'StoreHome',
    props: { title: 'Store', pretitle: 'Leiriacon 2022' },
    component: StoreHome,
  },
  {
    path: '/store/new',
    name: 'StoreAddGame',
    beforeEnter: guardAuthenticated,
    props: { title: 'Add game', pretitle: 'Store' },
    component: StoreAddGame,
  },
  {
    path: '/google-docs',
    name: 'GoogleDocs',
    props: { title: '', pretitle: '' },
    component: GoogleDocs,
  },
  {
    path: '/configurations',
    name: 'Configurations',
    props: { title: 'Configurations', pretitle: 'Admin' },
    beforeEnter: guardAuthenticated,
    component: Configurations,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    beforeEnter: (to, from, next) => {
      if (authorizationService.isAuthenticated()) {
        next({ name: 'NotFound' })
      } else {
        next()
      }
    },
  },
  {
    name: 'NotFound',
    path: '*',
    component: PageNotFound,
  },
]

const router = new VueRouter({
  mode: 'history',
  base: '/',
  routes,
})

export default router
