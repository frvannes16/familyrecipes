<template>
    <div style="overflow: auto;">
        <n-timeline horizontal size="large">
            <n-timeline-item title="Write Recipes" type="success" />
            <n-timeline-item title="Customize Cookbook" />
            <n-timeline-item title="Print & Pay" />
            <n-timeline-item title="Enjoy" />
        </n-timeline>
    </div>
</template>
  <script lang="ts">
import { defineComponent } from "vue";
import { NTimeline, NTimelineItem } from "naive-ui";

export default defineComponent({
    name: "ProgressBar",
    components: { NTimeline, NTimelineItem },
    props: {
        stage: {
            type: Number,
            required: true,
            default: 0
        }
    }
})
</script>