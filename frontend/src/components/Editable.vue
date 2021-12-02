<template>
    <div class="editable-wrapper" :style="`min-height: ${minHeight}; justify-content: ${justifyContent}`">
        <div class="slot">
            <slot
                name="edit"
                v-if="isEditing"
                @focusout.capture="() => toggleEditState(false)"
                :toggleEditState="toggleEditState"
            ></slot>
            <slot v-else :toggleEditState="toggleEditState"></slot>
        </div>
        <div class="button-group">
            <n-button
                tertiary
                circle
                type="error"
                #icon
                class="button"
                v-if="deleteButton"
                @click="onDeleteClick"
            >
                <n-icon>
                    <times-circle-regular />
                </n-icon>
            </n-button>
            <n-button circle #icon class="button" @click="() => toggleEditState(!isEditing)">
                <n-icon>
                    <check type="info" v-if="isEditing" />
                    <edit-regular v-else />
                </n-icon>
            </n-button>
        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent, ref, watch, onBeforeUnmount } from "vue";
import { NButton, NIcon } from "naive-ui";
import { Check, EditRegular, TimesCircleRegular } from "@vicons/fa";
import useEditGroup from "@/composables/useEditGroup";


const EDIT_COMPLETE_EVENT = "editComplete";
const EDIT_START_EVENT = "editStart";
const ON_DELETE_EVENT = "delete";

// This component allows any field to have two states, a preview state and an edit state.
// These two states make it easier to imply that a field can be edited and save on click away.
export default defineComponent({
    name: "Editable",
    components: { NButton, NIcon, Check, EditRegular, TimesCircleRegular },
    emits: [EDIT_START_EVENT, EDIT_COMPLETE_EVENT, ON_DELETE_EVENT],
    props: {
        minHeight: {
            type: String,
            required: false,
            default: "auto",
        },
        justifyContent: {
            type: String,
            required: false,
            default: "space-between",
        },
        deleteButton: {
            type: Boolean,
            required: false,
            default: false
        }
    },
    setup(props, context) {
        const isEditing = ref(false);

        const registerCallback = useEditGroup();  // Ensure that only one editable is in edit state at a time.
        const { deregisterCallback, claimFocus, relinquishFocus } = registerCallback(() => { toggleEditState(false) });
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

        const onDeleteClick = (event: Event) => {
            event.stopPropagation()
            context.emit(ON_DELETE_EVENT);
        }

        return {
            isEditing,
            toggleEditState,
            onDeleteClick,
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

.button-group {
    display: inherit;
}

.button-group > .button:not(:first-child) {
    margin-left: 4px;
}

.button {
    opacity: 0.3;
    transition: opacity 0.4s;
}

.editable-wrapper:hover .button {
    opacity: 1;
}
</style>