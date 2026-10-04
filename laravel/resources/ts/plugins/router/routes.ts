export const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', redirect: '/dashboard' },
  { path: '/register', redirect: '/dashboard' },
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    children: [
      {
        path: 'dashboard',
        component: () => import('@/pages/dashboard.vue'),
      },
      {
        path: 'production-capacity',
        component: () => import('@/pages/production-capacity.vue'),
      },
      {
        path: 'global-capacity',
        component: () => import('@/pages/global-capacity.vue'),
      },
      {
        path: 'forecasting-ai',
        component: () => import('@/pages/forecasting-ai.vue'),
      },
      {
        path: 'support-weather-mlops',
        component: () => import('@/pages/support-weather-mlops.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/blank.vue'),
    children: [
      {
        path: '/:pathMatch(.*)*',
        component: () => import('@/pages/[...error].vue'),
      },
    ],
  },
]

