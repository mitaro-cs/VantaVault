const REFRESH_INTERVAL_MS = 4000
const DEFAULT_SETTINGS = {
  preferred_volume_id: "",
  preferred_volume_name: "VantaVault",
  auto_open_preferred: true,
  notify_missing_preferred: true,
  open_in_file_manager_on_connect: false,
  failed_attempt_limit: 5,
  lockout_seconds: 900,
  encryption_default_name: "vault-backup",
}

class ApiError extends Error {
  constructor(message, data = {}, status = 500) {
    super(message)
    this.name = "ApiError"
    this.data = data
    this.status = status
  }
}

const state = {
  configured: false,
  authenticated: false,
  volumes: [],
  currentVolume: "",
  currentPath: "",
  items: [],
  filteredItems: [],
  lastVolume: "",
  preferredVolume: null,
  preferredConnected: false,
  settings: { ...DEFAULT_SETTINGS },
  failedAttempts: 0,
  failedAttemptLimit: DEFAULT_SETTINGS.failed_attempt_limit,
  lockoutRemainingSeconds: 0,
  lastPreferredConnected: null,
  pollingId: 0,
  refreshInFlight: false,
  actionModal: {
    open: false,
    mode: "encrypt",
    useVaultPassword: false,
    path: "",
    label: "",
    defaultName: "",
  },
}

const dom = {
  gate: document.getElementById("gate"),
  gateTitle: document.getElementById("gate-title"),
  gateCopy: document.getElementById("gate-copy"),
  authForm: document.getElementById("auth-form"),
  passwordInput: document.getElementById("password-input"),
  authSubmit: document.getElementById("auth-submit"),
  volumesList: document.getElementById("volumes-list"),
  signalChip: document.getElementById("signal-chip"),
  preferredVolumeName: document.getElementById("preferred-volume-name"),
  preferredVolumeCopy: document.getElementById("preferred-volume-copy"),
  preferredConnectionNote: document.getElementById("preferred-connection-note"),
  securityNote: document.getElementById("security-note"),
  focusPreferredBtn: document.getElementById("focus-preferred-btn"),
  openSettingsSide: document.getElementById("open-settings-side"),
  openSettingsTop: document.getElementById("open-settings-top"),
  heroVolumeName: document.getElementById("hero-volume-name"),
  heroPath: document.getElementById("hero-path"),
  heroVolumeBadge: document.getElementById("hero-volume-badge"),
  metricTotal: document.getElementById("metric-total"),
  metricFree: document.getElementById("metric-free"),
  metricItems: document.getElementById("metric-items"),
  storageUsedBar: document.getElementById("storage-used-bar"),
  itemsGrid: document.getElementById("items-grid"),
  breadcrumbs: document.getElementById("breadcrumbs"),
  searchInput: document.getElementById("search-input"),
  refreshVolumes: document.getElementById("refresh-volumes"),
  openFinder: document.getElementById("open-finder"),
  openCurrentBtn: document.getElementById("open-current-btn"),
  encryptCurrentBtn: document.getElementById("encrypt-current-btn"),
  recoveryBackupBtn: document.getElementById("recovery-backup-btn"),
  backBtn: document.getElementById("back-btn"),
  logoutBtn: document.getElementById("logout-btn"),
  securityStatusCopy: document.getElementById("security-status-copy"),
  encryptionStatusCopy: document.getElementById("encryption-status-copy"),
  attemptCounter: document.getElementById("attempt-counter"),
  lockoutCounter: document.getElementById("lockout-counter"),
  settingsModal: document.getElementById("settings-modal"),
  closeSettingsBtn: document.getElementById("close-settings-btn"),
  settingsForm: document.getElementById("settings-form"),
  preferredVolumeSelect: document.getElementById("preferred-volume-select"),
  preferredVolumeNameInput: document.getElementById("preferred-volume-name-input"),
  autoOpenPreferredInput: document.getElementById("auto-open-preferred-input"),
  notifyMissingPreferredInput: document.getElementById("notify-missing-preferred-input"),
  openInFileManagerOnConnectInput: document.getElementById("open-in-file-manager-on-connect-input"),
  failedAttemptLimitInput: document.getElementById("failed-attempt-limit-input"),
  lockoutSecondsInput: document.getElementById("lockout-seconds-input"),
  encryptionDefaultNameInput: document.getElementById("encryption-default-name-input"),
  actionModal: document.getElementById("action-modal"),
  closeActionBtn: document.getElementById("close-action-btn"),
  actionForm: document.getElementById("action-form"),
  actionModalEyebrow: document.getElementById("action-modal-eyebrow"),
  actionModalTitle: document.getElementById("action-modal-title"),
  actionModalCopy: document.getElementById("action-modal-copy"),
  actionNameField: document.getElementById("action-name-field"),
  actionNameLabel: document.getElementById("action-name-label"),
  actionNameInput: document.getElementById("action-name-input"),
  actionPasswordField: document.getElementById("action-password-field"),
  actionPasswordInput: document.getElementById("action-password-input"),
  actionSubmit: document.getElementById("action-submit"),
  toast: document.getElementById("toast"),
}

async function api(path, options = {}) {
  const config = {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "same-origin",
  }

  if (options.body !== undefined) {
    config.body = JSON.stringify(options.body)
  }

  const response = await fetch(path, config)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.ok === false) {
    throw new ApiError(data.error || "Произошла ошибка.", data, response.status)
  }
  return data
}

function showToast(message, isError = false) {
  if (!dom.toast) return
  dom.toast.hidden = false
  dom.toast.textContent = message
  dom.toast.dataset.error = isError ? "true" : "false"
  window.clearTimeout(showToast.timer)
  showToast.timer = window.setTimeout(() => {
    dom.toast.hidden = true
  }, 3200)
}

function formatDate(raw) {
  if (!raw) return ""
  const date = new Date(raw)
  if (Number.isNaN(date.getTime())) return ""
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
}

function selectedVolume() {
  return state.volumes.find((volume) => volume.id === state.currentVolume) || null
}

function preferredLabel() {
  if (state.preferredVolume?.name) return state.preferredVolume.name
  if (state.settings.preferred_volume_name) return state.settings.preferred_volume_name
  if (state.settings.preferred_volume_id) return state.settings.preferred_volume_id
  return "VantaVault"
}

function selectedItem(relativePath) {
  return state.items.find((item) => item.relative_path === relativePath) || null
}

function isArchiveItem(item) {
  return Boolean(item?.is_archive || item?.extension === ".zip")
}

function humanizeSeconds(value) {
  const seconds = Math.max(0, Number(value) || 0)
  if (!seconds) return "0 сек"
  if (seconds < 60) return `${seconds} сек`
  const minutes = Math.floor(seconds / 60)
  const restSeconds = seconds % 60
  if (minutes < 60) {
    return restSeconds ? `${minutes} мин ${restSeconds} сек` : `${minutes} мин`
  }
  const hours = Math.floor(minutes / 60)
  const restMinutes = minutes % 60
  return restMinutes ? `${hours} ч ${restMinutes} мин` : `${hours} ч`
}

function sanitizeComponentName(value, fallback) {
  const base = String(value || "").trim().replaceAll("\\", "/").split("/").pop() || fallback
  const cleaned = base.replace(/[<>:"|?*]/g, "-").trim().replace(/[.\s]+$/g, "")
  return cleaned || fallback
}

function defaultArchiveName(label) {
  const base = sanitizeComponentName(label, state.settings.encryption_default_name || "vault-backup")
  return base.toLowerCase().endsWith(".zip") ? base : `${base}.vvault.zip`
}

function defaultExtractName(label) {
  const name = sanitizeComponentName(label, "restored")
  if (name.toLowerCase().endsWith(".vvault.zip")) {
    return `${name.slice(0, -".vvault.zip".length)}-restored`
  }
  if (name.toLowerCase().endsWith(".zip")) {
    return `${name.slice(0, -".zip".length)}-restored`
  }
  return `${name}-restored`
}

function currentFolderLabel() {
  if (state.currentPath) {
    return state.currentPath.split("/").pop()
  }
  return selectedVolume()?.name || preferredLabel()
}

function applyStatusPayload(data) {
  if (!data || typeof data !== "object") return
  state.configured = Boolean(data.configured)
  state.authenticated = Boolean(data.authenticated)
  state.lastVolume = data.last_volume || ""
  state.failedAttempts = Number(data.failed_attempts || 0)
  state.failedAttemptLimit = Number(
    data.failed_attempt_limit || state.settings.failed_attempt_limit || DEFAULT_SETTINGS.failed_attempt_limit,
  )
  state.lockoutRemainingSeconds = Number(data.lockout_remaining_seconds || 0)
  state.preferredConnected = Boolean(data.preferred_volume_connected)
  state.preferredVolume = data.preferred_volume || null
  if (data.settings) {
    state.settings = {
      ...DEFAULT_SETTINGS,
      ...data.settings,
    }
  }
}

function syncCurrentVolume({ preferPreferred = false } = {}) {
  if (!state.volumes.length) {
    state.currentVolume = ""
    state.currentPath = ""
    return
  }

  if (preferPreferred && state.preferredConnected && state.preferredVolume) {
    state.currentVolume = state.preferredVolume.id
    state.currentPath = ""
    return
  }

  const currentExists = state.volumes.some((volume) => volume.id === state.currentVolume)
  if (currentExists) {
    return
  }

  const preferred = state.preferredConnected ? state.preferredVolume : null
  if (preferred) {
    state.currentVolume = preferred.id
    state.currentPath = ""
    return
  }

  const remembered = state.volumes.find((volume) => volume.id === state.lastVolume)
  state.currentVolume = remembered ? remembered.id : state.volumes[0].id
  state.currentPath = ""
}

function renderGate() {
  if (state.authenticated) {
    dom.gate.classList.add("hidden")
    return
  }

  dom.gate.classList.remove("hidden")
  dom.passwordInput.value = ""

  const diskReady = state.preferredConnected
  const locked = state.lockoutRemainingSeconds > 0

  if (state.configured) {
    dom.gateTitle.textContent = locked ? "Защита активна" : "Вход"
    if (locked) {
      dom.gateCopy.textContent =
        `Доступ временно заблокирован на ${humanizeSeconds(state.lockoutRemainingSeconds)}. Данные остаются на месте, автостирание отключено.`
    } else if (diskReady) {
      dom.gateCopy.textContent =
        `Диск ${preferredLabel()} уже подключен. Введи пароль, и vault откроется автоматически.`
    } else {
      dom.gateCopy.textContent =
        `Подключи диск ${preferredLabel()} к системе, затем разблокируй приложение локальным паролем.`
    }
    dom.authSubmit.textContent = "Открыть доступ"
  } else {
    dom.gateTitle.textContent = "Создай пароль"
    dom.gateCopy.textContent =
      "Первый пароль хранится локально и защищает доступ к приложению и recovery-функциям."
    dom.authSubmit.textContent = "Сохранить пароль"
  }

  dom.passwordInput.disabled = locked
  dom.authSubmit.disabled = locked
}

function renderPresence() {
  dom.preferredVolumeName.textContent = preferredLabel()
  dom.signalChip.textContent = state.preferredConnected ? "Онлайн" : "Ожидание"
  dom.signalChip.dataset.online = state.preferredConnected ? "true" : "false"
  dom.preferredConnectionNote.textContent = state.preferredConnected
    ? "Диск подключен"
    : "Подключи устройство"
  dom.securityNote.textContent = `${state.failedAttemptLimit} попыток и lockout`

  if (state.preferredConnected && state.preferredVolume) {
    dom.preferredVolumeCopy.textContent =
      `Обнаружен диск ${state.preferredVolume.name}. Его можно открыть в приложении автоматически или вручную через настройки.`
  } else {
    dom.preferredVolumeCopy.textContent =
      `Целевой диск ${preferredLabel()} не найден. Подключи его к системе, и VantaVault предложит открыть vault.`
  }

  dom.focusPreferredBtn.disabled = !(state.authenticated && state.preferredConnected)
}

function renderVolumes() {
  if (!state.authenticated) {
    dom.volumesList.innerHTML =
      '<div class="empty-card">После разблокировки здесь появятся все подключенные диски.</div>'
    return
  }

  if (!state.volumes.length) {
    dom.volumesList.innerHTML =
      '<div class="empty-card">Подключи внешний диск, и он появится в списке.</div>'
    return
  }

  const preferredId = state.preferredVolume?.id || state.settings.preferred_volume_id

  dom.volumesList.innerHTML = state.volumes
    .map((volume) => {
      const active = volume.id === state.currentVolume
      const preferred = volume.id === preferredId
      return `
        <button class="volume-card ${active ? "active" : ""}" type="button" data-volume="${escapeHtml(volume.id)}">
          <div>
            <strong>${escapeHtml(volume.name)}</strong>
            <span>${escapeHtml(volume.free_label)} свободно</span>
          </div>
          <div class="volume-meta">
            ${preferred ? '<small class="volume-default">Default</small>' : ""}
            <small>${escapeHtml(volume.total_label)}</small>
          </div>
        </button>
      `
    })
    .join("")
}

function renderHero() {
  const volume = selectedVolume()
  const total = volume ? volume.total_bytes : 0
  const used = volume ? volume.used_bytes : 0
  const usedPercent = total > 0 ? Math.max(6, Math.round((used / total) * 100)) : 0

  dom.heroVolumeName.textContent = volume ? volume.name : "Нет диска"
  dom.heroPath.textContent = state.currentPath ? `/${state.currentPath}` : "/"
  dom.heroVolumeBadge.textContent = volume
    ? state.preferredConnected && state.preferredVolume?.id === volume.id
      ? "VantaVault online"
      : "Подключен"
    : "Ожидание"
  dom.metricTotal.textContent = volume ? volume.total_label : "-"
  dom.metricFree.textContent = volume ? volume.free_label : "-"
  dom.metricItems.textContent = String(
    state.filteredItems.length || state.items.length || 0,
  )
  dom.storageUsedBar.style.width = volume ? `${usedPercent}%` : "0%"
}

function renderSecurityPanel() {
  dom.attemptCounter.textContent = `${state.failedAttempts} / ${state.failedAttemptLimit}`
  dom.lockoutCounter.textContent =
    state.lockoutRemainingSeconds > 0
      ? humanizeSeconds(state.lockoutRemainingSeconds)
      : "Не активен"

  if (state.lockoutRemainingSeconds > 0) {
    dom.securityStatusCopy.textContent =
      `После серии неверных попыток вход заморожен на ${humanizeSeconds(state.lockoutRemainingSeconds)}. Данные не стираются автоматически.`
  } else if (state.failedAttempts > 0) {
    dom.securityStatusCopy.textContent =
      `Есть неудачные попытки входа: ${state.failedAttempts}. После достижения лимита включится временная блокировка.`
  } else {
    dom.securityStatusCopy.textContent =
      "Защита в норме. Неверные пароли считают попытки и переводят vault в lockout, а не в режим уничтожения данных."
  }

  dom.encryptionStatusCopy.textContent =
    "Для файлов и папок доступны AES-архивы. Recovery-архив использует пароль текущей сессии, если ты уже вошел в vault."
}

function renderBreadcrumbs() {
  const volume = selectedVolume()
  if (!state.currentVolume) {
    dom.breadcrumbs.innerHTML = ""
    return
  }

  const parts = []
  parts.push(
    `<button type="button" data-path="">${escapeHtml(volume ? volume.name : "Диск")}</button>`,
  )
  if (state.currentPath) {
    const segments = state.currentPath.split("/")
    let current = ""
    for (const segment of segments) {
      current = current ? `${current}/${segment}` : segment
      parts.push(
        `<button type="button" data-path="${escapeHtml(current)}">${escapeHtml(segment)}</button>`,
      )
    }
  }
  dom.breadcrumbs.innerHTML = parts.join('<span class="crumb-sep">/</span>')
}

function renderItems() {
  const items =
    state.filteredItems.length || dom.searchInput.value.trim()
      ? state.filteredItems
      : state.items

  if (!state.authenticated) {
    dom.itemsGrid.innerHTML =
      '<div class="empty-card empty-large">Разблокируй приложение, чтобы просматривать содержимое диска.</div>'
    return
  }

  if (!state.currentVolume) {
    dom.itemsGrid.innerHTML =
      '<div class="empty-card empty-large">Выбери диск слева или дождись подключения целевого устройства.</div>'
    return
  }

  if (!items.length) {
    dom.itemsGrid.innerHTML =
      '<div class="empty-card empty-large">В этой папке ничего нет.</div>'
    return
  }

  dom.itemsGrid.innerHTML = items
    .map((item) => {
      const typeLabel = item.is_dir ? "Папка" : item.extension || "Файл"
      const meta = item.is_dir ? typeLabel : `${typeLabel} · ${item.size_label || "-"}`
      const toolLabel = isArchiveItem(item) ? "Распаковать" : "AES архив"
      const toolAttr = isArchiveItem(item) ? "data-decrypt" : "data-encrypt"
      return `
        <article class="item-card" data-path="${escapeHtml(item.relative_path)}" data-dir="${item.is_dir ? "true" : "false"}">
          <div class="item-icon">${item.is_dir ? "D" : isArchiveItem(item) ? "Z" : "F"}</div>
          <div class="item-copy">
            <strong>${escapeHtml(item.name)}</strong>
            <span>${escapeHtml(meta)}</span>
            <small>${escapeHtml(formatDate(item.modified_at))}</small>
          </div>
          <div class="item-actions">
            <button class="item-open-btn" type="button" data-open="${escapeHtml(item.relative_path)}">
              ${item.is_dir ? "Открыть" : "Показать"}
            </button>
            <button
              class="item-tool-btn"
              type="button"
              ${toolAttr}="${escapeHtml(item.relative_path)}"
              data-label="${escapeHtml(item.name)}"
            >
              ${toolLabel}
            </button>
          </div>
        </article>
      `
    })
    .join("")
}

function renderSettingsForm() {
  if (!dom.preferredVolumeSelect) return

  const options = [
    '<option value="">Определять по имени диска</option>',
    ...state.volumes.map(
      (volume) =>
        `<option value="${escapeHtml(volume.id)}">${escapeHtml(volume.name)} · ${escapeHtml(volume.total_label)}</option>`,
    ),
  ]

  dom.preferredVolumeSelect.innerHTML = options.join("")
  dom.preferredVolumeSelect.value = state.settings.preferred_volume_id || ""
  dom.preferredVolumeNameInput.value = state.settings.preferred_volume_name || ""
  dom.autoOpenPreferredInput.checked = Boolean(state.settings.auto_open_preferred)
  dom.notifyMissingPreferredInput.checked = Boolean(state.settings.notify_missing_preferred)
  dom.openInFileManagerOnConnectInput.checked = Boolean(
    state.settings.open_in_file_manager_on_connect,
  )
  dom.failedAttemptLimitInput.value = String(state.settings.failed_attempt_limit)
  dom.lockoutSecondsInput.value = String(state.settings.lockout_seconds)
  dom.encryptionDefaultNameInput.value = state.settings.encryption_default_name || "vault-backup"
}

function renderActionModal() {
  if (!state.actionModal.open) {
    dom.actionModal.classList.add("hidden")
    return
  }

  const label = state.actionModal.label || currentFolderLabel()
  if (state.actionModal.mode === "encrypt") {
    dom.actionModalEyebrow.textContent = state.actionModal.useVaultPassword
      ? "Recovery archive"
      : "AES archive"
    dom.actionModalTitle.textContent = state.actionModal.useVaultPassword
      ? "Recovery-архив"
      : "Создать AES-архив"
    dom.actionModalCopy.textContent = state.actionModal.useVaultPassword
      ? `Будет создан зашифрованный recovery-архив для "${label}" с паролем текущей сессии vault.`
      : `Создай AES-архив для "${label}" и задай отдельный пароль архива.`
    dom.actionNameField.hidden = false
    dom.actionNameLabel.textContent = "Имя архива"
    dom.actionNameInput.value = state.actionModal.defaultName || defaultArchiveName(label)
    dom.actionPasswordField.hidden = state.actionModal.useVaultPassword
    dom.actionPasswordInput.value = ""
    dom.actionSubmit.textContent = state.actionModal.useVaultPassword
      ? "Создать recovery-архив"
      : "Создать AES-архив"
  } else {
    dom.actionModalEyebrow.textContent = "Decrypt archive"
    dom.actionModalTitle.textContent = "Распаковать архив"
    dom.actionModalCopy.textContent = `Распакуй архив "${label}" в новую папку внутри текущего диска.`
    dom.actionNameField.hidden = false
    dom.actionNameLabel.textContent = "Имя папки"
    dom.actionNameInput.value = state.actionModal.defaultName || defaultExtractName(label)
    dom.actionPasswordField.hidden = false
    dom.actionPasswordInput.value = ""
    dom.actionSubmit.textContent = "Распаковать архив"
  }

  dom.actionModal.classList.remove("hidden")
}

function renderAll() {
  renderGate()
  renderPresence()
  renderVolumes()
  renderHero()
  renderSecurityPanel()
  renderBreadcrumbs()
  renderItems()
  renderSettingsForm()
  renderActionModal()
}

function applySearch() {
  const query = dom.searchInput.value.trim().toLowerCase()
  if (!query) {
    state.filteredItems = []
  } else {
    state.filteredItems = state.items.filter((item) =>
      item.name.toLowerCase().includes(query),
    )
  }
  renderHero()
  renderItems()
}

async function refreshStatus() {
  const data = await api("/api/status")
  applyStatusPayload(data)
  if (!state.authenticated) {
    state.volumes = []
    state.currentVolume = ""
    state.currentPath = ""
    state.items = []
    state.filteredItems = []
  }
  renderAll()
}

async function openVolumeTarget(volumeId, path = "") {
  await api("/api/open", {
    method: "POST",
    body: {
      volume: volumeId,
      path,
    },
  })
}

async function browse(volumeId, relativePath = "") {
  const params = new URLSearchParams({
    volume: volumeId,
    path: relativePath,
  })
  const data = await api(`/api/browse?${params.toString()}`)
  state.currentVolume = volumeId
  state.currentPath = data.listing.current_path || ""
  state.items = data.listing.items || []
  state.filteredItems = []
  dom.searchInput.value = ""
  renderAll()
}

async function maybeHandlePreferredTransition(previousConnected, previousPreferredId) {
  if (previousConnected === null) {
    state.lastPreferredConnected = state.preferredConnected
    return
  }

  if (!previousConnected && state.preferredConnected) {
    showToast(`Диск ${preferredLabel()} подключен.`)
    if (
      state.settings.open_in_file_manager_on_connect &&
      state.preferredVolume &&
      state.authenticated
    ) {
      try {
        await openVolumeTarget(state.preferredVolume.id, "")
      } catch (error) {
        showToast(error.message, true)
      }
    }
  }

  if (previousConnected && !state.preferredConnected && state.settings.notify_missing_preferred) {
    const missingLabel =
      previousPreferredId && previousPreferredId === state.currentVolume
        ? preferredLabel()
        : preferredLabel()
    showToast(`Подключи диск ${missingLabel} к системе.`, true)
  }

  state.lastPreferredConnected = state.preferredConnected
}

async function loadVolumes({ auto = false } = {}) {
  const previousConnected = state.lastPreferredConnected
  const previousPreferredId = state.preferredVolume?.id || state.settings.preferred_volume_id
  const data = await api("/api/volumes")
  applyStatusPayload(data)
  state.volumes = data.volumes || []

  const shouldPreferPreferred =
    state.authenticated &&
    state.preferredConnected &&
    state.settings.auto_open_preferred &&
    (previousConnected === false || !state.currentVolume || !state.volumes.some((volume) => volume.id === state.currentVolume))

  syncCurrentVolume({ preferPreferred: shouldPreferPreferred })

  if (state.currentVolume) {
    try {
      await browse(state.currentVolume, state.currentPath || "")
    } catch (error) {
      if (state.currentPath) {
        state.currentPath = ""
        await browse(state.currentVolume, "")
        showToast("Текущая папка недоступна. Открыт корень диска.")
      } else {
        throw error
      }
    }
  } else {
    state.items = []
    state.filteredItems = []
    renderAll()
  }

  await maybeHandlePreferredTransition(previousConnected, previousPreferredId)

  if (auto && !state.preferredConnected && state.settings.notify_missing_preferred) {
    dom.signalChip.dataset.missing = "true"
  } else {
    delete dom.signalChip.dataset.missing
  }
}

async function focusPreferredVolume() {
  if (!state.authenticated || !state.preferredConnected || !state.preferredVolume) {
    showToast("Подключи и разблокируй целевой диск.", true)
    return
  }
  await browse(state.preferredVolume.id, "")
}

function openSettingsModal() {
  if (!state.authenticated) {
    showToast("Сначала разблокируй приложение.", true)
    return
  }
  renderSettingsForm()
  dom.settingsModal.classList.remove("hidden")
}

function closeSettingsModal() {
  dom.settingsModal.classList.add("hidden")
}

function openEncryptModal(path, label, { useVaultPassword = false } = {}) {
  state.actionModal = {
    open: true,
    mode: "encrypt",
    useVaultPassword,
    path,
    label,
    defaultName: defaultArchiveName(label || currentFolderLabel()),
  }
  renderActionModal()
}

function openDecryptModal(path, label) {
  state.actionModal = {
    open: true,
    mode: "decrypt",
    useVaultPassword: false,
    path,
    label,
    defaultName: defaultExtractName(label),
  }
  renderActionModal()
}

function closeActionModal() {
  state.actionModal.open = false
  renderActionModal()
}

async function onAuthSubmit(event) {
  event.preventDefault()
  const password = dom.passwordInput.value.trim()
  if (!password) {
    showToast("Введите пароль.", true)
    return
  }

  const wasConfigured = state.configured
  const route = wasConfigured ? "/api/login" : "/api/setup"
  const data = await api(route, {
    method: "POST",
    body: { password },
  })
  applyStatusPayload(data)
  state.authenticated = true
  renderAll()
  await loadVolumes()
  showToast(wasConfigured ? "Доступ открыт." : "Пароль сохранен.")
}

async function onLogout() {
  await api("/api/logout", { method: "POST", body: {} })
  state.authenticated = false
  state.currentVolume = ""
  state.currentPath = ""
  state.items = []
  state.filteredItems = []
  state.volumes = []
  await refreshStatus()
  showToast("Приложение заблокировано.")
}

async function onSaveSettings(event) {
  event.preventDefault()
  const payload = {
    preferred_volume_id: dom.preferredVolumeSelect.value,
    preferred_volume_name: dom.preferredVolumeNameInput.value.trim() || preferredLabel(),
    auto_open_preferred: dom.autoOpenPreferredInput.checked,
    notify_missing_preferred: dom.notifyMissingPreferredInput.checked,
    open_in_file_manager_on_connect: dom.openInFileManagerOnConnectInput.checked,
    failed_attempt_limit: Number(dom.failedAttemptLimitInput.value),
    lockout_seconds: Number(dom.lockoutSecondsInput.value),
    encryption_default_name: dom.encryptionDefaultNameInput.value.trim() || "vault-backup",
  }

  const data = await api("/api/settings", {
    method: "POST",
    body: payload,
  })
  applyStatusPayload(data)
  state.volumes = data.volumes || state.volumes
  closeSettingsModal()
  renderAll()
  await loadVolumes()
  showToast("Настройки сохранены.")
}

async function onActionSubmit(event) {
  event.preventDefault()
  if (!state.currentVolume) {
    showToast("Сначала выбери диск.", true)
    return
  }

  const name = dom.actionNameInput.value.trim()
  const password = dom.actionPasswordInput.value.trim()

  if (state.actionModal.mode === "encrypt") {
    if (!state.actionModal.useVaultPassword && !password) {
      showToast("Введите пароль архива.", true)
      return
    }

    await api("/api/encrypt", {
      method: "POST",
      body: {
        volume: state.currentVolume,
        path: state.actionModal.path,
        archive_name: name,
        password,
        use_vault_password: state.actionModal.useVaultPassword,
      },
    })
    closeActionModal()
    await browse(state.currentVolume, state.currentPath || "")
    showToast(
      state.actionModal.useVaultPassword
        ? "Recovery-архив создан."
        : "AES-архив создан.",
    )
    return
  }

  if (!password) {
    showToast("Введите пароль архива.", true)
    return
  }

  await api("/api/decrypt", {
    method: "POST",
    body: {
      volume: state.currentVolume,
      path: state.actionModal.path,
      output_name: name,
      password,
    },
  })
  closeActionModal()
  await browse(state.currentVolume, state.currentPath || "")
  showToast("Архив распакован.")
}

function bindEvents() {
  dom.authForm.addEventListener("submit", async (event) => {
    try {
      await onAuthSubmit(event)
    } catch (error) {
      if (error instanceof ApiError) {
        applyStatusPayload(error.data)
        renderAll()
      }
      showToast(error.message, true)
    }
  })

  dom.refreshVolumes.addEventListener("click", async () => {
    try {
      await loadVolumes()
      showToast("Список дисков обновлен.")
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.logoutBtn.addEventListener("click", async () => {
    try {
      await onLogout()
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.openFinder.addEventListener("click", async () => {
    try {
      if (!state.currentVolume) {
        showToast("Сначала выбери диск.", true)
        return
      }
      await openVolumeTarget(state.currentVolume, "")
      showToast("Диск открыт в файловом менеджере.")
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.openCurrentBtn.addEventListener("click", async () => {
    try {
      if (!state.currentVolume) {
        showToast("Сначала выбери диск.", true)
        return
      }
      await openVolumeTarget(state.currentVolume, state.currentPath)
      showToast("Текущая папка открыта.")
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.encryptCurrentBtn.addEventListener("click", () => {
    if (!state.currentVolume) {
      showToast("Сначала выбери диск.", true)
      return
    }
    openEncryptModal(state.currentPath, currentFolderLabel(), { useVaultPassword: false })
  })

  dom.recoveryBackupBtn.addEventListener("click", () => {
    if (!state.currentVolume) {
      showToast("Сначала выбери диск.", true)
      return
    }
    openEncryptModal(state.currentPath, currentFolderLabel(), { useVaultPassword: true })
  })

  dom.backBtn.addEventListener("click", async () => {
    if (!state.currentPath) return
    const parts = state.currentPath.split("/")
    parts.pop()
    try {
      await browse(state.currentVolume, parts.join("/"))
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.searchInput.addEventListener("input", applySearch)

  dom.volumesList.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-volume]")
    if (!button) return
    try {
      await browse(button.dataset.volume, "")
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.breadcrumbs.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-path]")
    if (!button || !state.currentVolume) return
    try {
      await browse(state.currentVolume, button.dataset.path || "")
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.itemsGrid.addEventListener("click", async (event) => {
    const openButton = event.target.closest("[data-open]")
    if (openButton) {
      try {
        await openVolumeTarget(state.currentVolume, openButton.dataset.open || "")
        showToast("Открыто в файловом менеджере.")
      } catch (error) {
        showToast(error.message, true)
      }
      return
    }

    const encryptButton = event.target.closest("[data-encrypt]")
    if (encryptButton) {
      openEncryptModal(
        encryptButton.dataset.encrypt || "",
        encryptButton.dataset.label || "item",
        { useVaultPassword: false },
      )
      return
    }

    const decryptButton = event.target.closest("[data-decrypt]")
    if (decryptButton) {
      openDecryptModal(
        decryptButton.dataset.decrypt || "",
        decryptButton.dataset.label || "archive",
      )
      return
    }

    const card = event.target.closest("[data-path][data-dir='true']")
    if (!card || !state.currentVolume) return
    try {
      await browse(state.currentVolume, card.dataset.path || "")
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.focusPreferredBtn.addEventListener("click", async () => {
    try {
      await focusPreferredVolume()
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.openSettingsSide.addEventListener("click", openSettingsModal)
  dom.openSettingsTop.addEventListener("click", openSettingsModal)
  dom.closeSettingsBtn.addEventListener("click", closeSettingsModal)
  dom.closeActionBtn.addEventListener("click", closeActionModal)
  dom.settingsForm.addEventListener("submit", async (event) => {
    try {
      await onSaveSettings(event)
    } catch (error) {
      showToast(error.message, true)
    }
  })

  dom.preferredVolumeSelect.addEventListener("change", () => {
    const selected = state.volumes.find(
      (volume) => volume.id === dom.preferredVolumeSelect.value,
    )
    if (selected) {
      dom.preferredVolumeNameInput.value = selected.name
    }
  })

  dom.actionForm.addEventListener("submit", async (event) => {
    try {
      await onActionSubmit(event)
    } catch (error) {
      showToast(error.message, true)
    }
  })

  document.addEventListener("click", (event) => {
    const closeTarget = event.target.closest("[data-close-modal]")
    if (!closeTarget) return
    const modalName = closeTarget.dataset.closeModal
    if (modalName === "settings") {
      closeSettingsModal()
    } else if (modalName === "action") {
      closeActionModal()
    }
  })
}

async function pollAppState() {
  if (state.refreshInFlight) return
  state.refreshInFlight = true
  try {
    if (state.authenticated) {
      await loadVolumes({ auto: true })
    } else {
      await refreshStatus()
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      applyStatusPayload(error.data)
      state.authenticated = false
      renderAll()
      return
    }
    console.error(error)
  } finally {
    state.refreshInFlight = false
  }
}

function startPolling() {
  if (state.pollingId) return
  state.pollingId = window.setInterval(() => {
    void pollAppState()
  }, REFRESH_INTERVAL_MS)
}

async function init() {
  bindEvents()
  renderAll()
  try {
    await refreshStatus()
    if (state.authenticated) {
      await loadVolumes()
    }
  } catch (error) {
    showToast(error.message, true)
  }
  startPolling()
}

void init()
