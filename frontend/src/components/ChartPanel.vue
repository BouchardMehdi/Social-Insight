<script setup lang="ts">
import {
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  DoughnutController,
  Filler,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
  ArcElement,
  type ChartConfiguration,
} from 'chart.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

Chart.register(
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  DoughnutController,
  Filler,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
)

const props = defineProps<{
  title: string
  config: ChartConfiguration
}>()

const canvas = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function renderChart() {
  if (!canvas.value) return
  chart?.destroy()
  chart = new Chart(canvas.value, props.config)
}

onMounted(renderChart)
onBeforeUnmount(() => chart?.destroy())
watch(() => props.config, renderChart, { deep: true })
</script>

<template>
  <section class="chart-panel">
    <header>
      <h2>{{ title }}</h2>
    </header>
    <div class="chart-frame">
      <canvas ref="canvas"></canvas>
    </div>
  </section>
</template>
