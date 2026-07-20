<script setup>
import { AlertTriangle, X } from 'lucide-vue-next'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  isDestructive: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['confirm', 'cancel'])

function onConfirm() {
  emit('confirm')
}

function onCancel() {
  emit('cancel')
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="onCancel">
    <div class="modal-container glass-panel">
      <div class="modal-header">
        <div class="modal-title">
          <AlertTriangle v-if="isDestructive" size="20" class="icon-warning" />
          <h2>{{ title }}</h2>
        </div>
        <button class="btn-close" @click="onCancel">
          <X size="20" />
        </button>
      </div>
      
      <div class="modal-body">
        <p>{{ message }}</p>
      </div>
      
      <div class="modal-footer">
        <button class="btn-cancel" @click="onCancel">{{ cancelText }}</button>
        <button 
          class="btn-confirm" 
          :class="{ 'destructive': isDestructive }" 
          @click="onConfirm"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-container {
  width: 100%;
  max-width: 420px;
  background: var(--bg-card, var(--bg-panel));
  border: 1px solid var(--border-color);


  display: flex;
  flex-direction: column;
  animation: modal-enter 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes modal-enter {
  0% { opacity: 0; transform: scale(0.95) translateY(10px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-title h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-main);
}

.icon-warning {
  color: var(--accent-red);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;

  transition: all 0.2s;
}
.btn-close:hover {
  background: var(--overlay-10);
  color: var(--text-main);
}

.modal-body {
  padding: 20px;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.modal-body p {
  margin: 0;
}

.modal-footer {
  padding: 16px 20px;
  background: var(--bg-panel);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 8px 16px;

  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-cancel:hover {
  background: var(--overlay-8);
}

.btn-confirm {
  background: var(--accent-orange);
  border: none;
  color: #fff;
  padding: 8px 16px;

  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-confirm:hover {
  filter: brightness(1.1);
}

.btn-confirm.destructive {
  background: var(--accent-red);
}
.btn-confirm.destructive:hover {
  background: #dc2626;
}
</style>
