<template>
    <div class="editable-wrapper" :style="`height: ${height}; justify-content: ${justifyContent}`">
        <div class="slot">
            <slot
                name="edit"
                v-if="isEditing"
                @focusout.capture="() => toggleEditState(false)"
                :toggleEditState="toggleEditState"
            ></slot>
            <slot v-else :toggleEditState="toggleEditState"></slot>
        </div>
        <div @click="() => toggleEditState(!isEditing)" class="button">
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
import { defineComponent, defineExpose, ref, watch, onBeforeUnmount } from "vue";
import { NButton, NIcon } from "naive-ui";
import { Check, EditRegular } from "@vicons/fa";
import useEditGroup from "@/composables/useEditGroup";


const EDIT_COMPLETE_EVENT = "editComplete";
const EDIT_START_EVENT = "editStart";

// This component allows any field to have two states, a preview state and an edit state.
// These two states make it easier to imply that a field can be edited and save on click away.
export default defineComponent({
    name: "Editable",
    components: { NButton, NIcon, Check, EditRegular },
    emits: [EDIT_START_EVENT, EDIT_COMPLETE_EVENT],
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

        const registerCallback = useEditGroup();  // Ensure that only one editable is in edit state at a time.
        const {deregisterCallback, claimFocus, relinquishFocus} = registerCallback(() => {toggleEditState(false)});
        onBeforeUnmount(deregisterCallback);

        const toggleEditState = (newState: boolean) => {
            isEditing.value = newState;
            if (newState == true) {
                claimFocus(); // Ensures other editables hide their edit slot.
            } else {
                relinquishFocus();
            }
        };

        watch(isEditing, (editState) => {
            context.emit(editState ? EDIT_START_EVENT : EDIT_COMPLETE_EVENT);
        });

        return {
            isEditing,
            toggleEditState,
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