import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import RobotsView from "../views/RobotsView.vue";
import TasksView from "../views/TasksView.vue";
import EventsView from "../views/EventsView.vue";

import UserApp from "../views/user/UserApp.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "overview",
      component: HomeView, // 우리가 Summary 띄우는 화면
    },
    {
      path: "/robots",
      name: "robots",
      component: RobotsView,
    },
    {
      path: "/tasks",
      name: "tasks",
      component: TasksView,
    },
    {
      path: "/events",
      name: "events",
      component: EventsView,
    },

    { 
      path: "/user", 
      name: "user", 
      component: UserApp
    },
  ],
});

export default router;
