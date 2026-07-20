<script setup>
defineProps({
  request: { type: Object, required: true }
})

const emit = defineEmits(['close'])
</script>

<template>
  <div class="auth-overlay" @click="emit('close')">
    <div class="request-modal glass-panel" @click.stop>
      <div class="modal-header">
        <h3>Request Details</h3>
        <button class="btn-close" @click="emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <div class="req-section">
          <h4>URL</h4>
          <div class="code-block">{{ request.request?.request?.url || 'N/A' }}</div>
        </div>

        <div class="req-section" v-if="request.request?.request?.headers">
          <h4>Request Headers</h4>
          <pre class="code-block">{{ JSON.stringify(request.request.request.headers, null, 2) }}</pre>
        </div>

        <div class="req-section" v-if="request.response?.response?.headers || request.request?.response?.headers">
          <h4>Response Headers</h4>
          <pre class="code-block">{{ JSON.stringify(request.response?.response?.headers || request.request?.response?.headers, null, 2) }}</pre>
        </div>

        <div class="req-section" v-if="request.request?.request?.postData">
          <h4>Payload / PostData</h4>
          <pre class="code-block">{{ typeof request.request.request.postData === 'string' ? request.request.request.postData : JSON.stringify(request.request.request.postData, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 40px;
}

.request-modal {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);

  border: 1px solid var(--border-color);

}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--accent-orange);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--text-main);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.req-section h4 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.code-block {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  padding: 12px;

  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--text-main);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}
</style>
