<template>
    <div class="editable-wrapper" :style="`height: ${height}; justify-content: ${justifyContent}`">
        <div class="slot">
            <slot
                name="edit-state"
                v-if="isEditing"
                @blur.capture="isEditing = false"
                :toggleEditState="toggleEditState"
            ></slot>
            <slot v-else :toggleEditState="toggleEditState"></slot>
        </div>
        <div @click="isEditing = !isEditing" class="button">
            <n-button circle>
                <template #icon>
                    <n-icon>
                        <check v-if="isEditing" />
                        <edit-regular v-else />
                    </n-icon>
                </template>
            </n-button>
        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent, ref, watch } from "vue";
import { NButton, NIcon } from "naive-ui";
import { Check, EditRegular } from "@vicons/fa";


const EDIT_COMPLETE_EVENT = "editComplete";

// This component allows any field to have two states, a preview state and an edit state.
// These two states make it easier to imply that a field can be edited and save on click away.
export default defineComponent({
    name: "Editable",
    components: { NButton, NIcon, Check, EditRegular },
    emits: [EDIT_COMPLETE_EVENT],
    props: {
        height: {
            type: String,
            required: false,
            default: "auto",
        },
        justifyContent: {
            type: String,
            required: false,
            default: "space-between",
        }
    },
    setup(props, context) {
        const isEditing = ref(false);
        const toggleEditState = (newState: boolean) => {
            isEditing.value = newState;
        };

        watch(isEditing, (editState) => {
           if (editState == false)  {
               context.emit(EDIT_COMPLETE_EVENT);
           }
        });

        return {
            isEditing,
            toggleEditState
        };

    },
});
</script>
<style scoped>
.editable-wrapper {
    display: flex;
    flex-direction: row;
    align-items: center;
}
.slot {
    flex-grow: 1;
    width: 85%;
    padding-right: 12px;
}

.button {
    opacity: 0.3;
    transition: opacity 0.4s;
    width: 15%;
}

.editable-wrapper:hover .button {
    opacity: 1;
}
</style>