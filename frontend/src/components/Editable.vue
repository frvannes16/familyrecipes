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
        <n-button circle @click="isEditing = !isEditing" class="button">
            <template #icon>
                <n-icon>
                    <check v-if="isEditing" />
                    <edit-regular v-else />
                </n-icon>
            </template>
        </n-button>
    </div>
</template>
<script lang="ts">
import { defineComponent } from "vue";
import { NButton, NIcon } from "naive-ui";
import { Check, EditRegular } from "@vicons/fa";


const EDIT_COMPLETE_EVENT = "editComplete";

// This component allows any field to have two states, a preview state and an edit state.
// These two states make it easier to imply that a field can be edited and save on click away.
export default defineComponent({
    name: "Editable",
    components: { NButton, NIcon, Check, EditRegular },
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
    data() {
        return {
            isEditing: false as Boolean,
        }
    },
    methods: {
        toggleEditState(newState: boolean) {
            // called by the slots children when the user is done editing the field. 
            // Usually called on blur events.
            this.isEditing = newState;

        }
    },
    watch: {
        isEditing(newValue) {
            if (newValue == false) {
                this.$emit(EDIT_COMPLETE_EVENT);
            }
        }
    }

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
    margin-right: 24px;
}

.button {
    opacity: 0.3;
    transition: opacity 0.4s;
}

.editable-wrapper:hover .button {
    opacity: 1;
}
</style>