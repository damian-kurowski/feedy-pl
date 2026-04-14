<script setup lang="ts">
import { onBeforeUnmount, watch } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import api from '../api/client'
import { useToast, getApiError } from '../composables/useToast'

const props = defineProps<{ modelValue: string | undefined }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const toast = useToast()

const editor = useEditor({
  content: props.modelValue || '<p></p>',
  extensions: [
    StarterKit.configure({
      heading: { levels: [2, 3, 4] },
    }),
    Link.configure({
      openOnClick: false,
      autolink: true,
      HTMLAttributes: { rel: 'noopener nofollow', target: '_blank' },
    }),
    Image.configure({
      inline: false,
      HTMLAttributes: { class: 'rounded-xl' },
    }),
  ],
  editorProps: {
    attributes: {
      class: 'blog-prose focus:outline-none min-h-[280px]',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(() => props.modelValue, (val) => {
  if (!editor.value) return
  if (val !== editor.value.getHTML()) {
    editor.value.commands.setContent(val || '<p></p>', { emitUpdate: false })
  }
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

function setLink() {
  if (!editor.value) return
  const previous = editor.value.getAttributes('link').href || ''
  const url = window.prompt('Adres URL (puste = usuń link):', previous)
  if (url === null) return
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

async function uploadImage(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length || !editor.value) return
  try {
    const formData = new FormData()
    formData.append('file', input.files[0])
    const { data } = await api.post('/images/upload', formData)
    editor.value.chain().focus().setImage({ src: data.url, alt: '' }).run()
  } catch (e) {
    toast.error(getApiError(e, 'Nie udało się wgrać obrazka'))
  } finally {
    input.value = ''
  }
}

const btnBase = 'h-8 px-2.5 text-xs font-medium border border-gray-200 hover:border-indigo-400 rounded-md transition cursor-pointer flex items-center gap-1'
function btnClass(active: boolean) {
  return active ? `${btnBase} bg-indigo-600 text-white border-indigo-600` : `${btnBase} bg-white text-gray-700`
}
</script>

<template>
  <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
    <!-- Toolbar -->
    <div v-if="editor" class="flex flex-wrap items-center gap-1 p-2 border-b border-gray-200 bg-gray-50">
      <button type="button" :class="btnClass(editor.isActive('heading', { level: 2 }))"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" title="Nagłówek H2">H2</button>
      <button type="button" :class="btnClass(editor.isActive('heading', { level: 3 }))"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" title="Nagłówek H3">H3</button>
      <button type="button" :class="btnClass(editor.isActive('paragraph'))"
        @click="editor.chain().focus().setParagraph().run()" title="Akapit">P</button>
      <span class="w-px h-5 bg-gray-300 mx-1"></span>

      <button type="button" :class="btnClass(editor.isActive('bold'))"
        @click="editor.chain().focus().toggleBold().run()" title="Pogrubienie (Ctrl+B)">
        <strong>B</strong>
      </button>
      <button type="button" :class="btnClass(editor.isActive('italic'))"
        @click="editor.chain().focus().toggleItalic().run()" title="Kursywa (Ctrl+I)">
        <em>I</em>
      </button>
      <button type="button" :class="btnClass(editor.isActive('strike'))"
        @click="editor.chain().focus().toggleStrike().run()" title="Przekreślenie">
        <s>S</s>
      </button>
      <span class="w-px h-5 bg-gray-300 mx-1"></span>

      <button type="button" :class="btnClass(editor.isActive('bulletList'))"
        @click="editor.chain().focus().toggleBulletList().run()" title="Lista punktowana">• Lista</button>
      <button type="button" :class="btnClass(editor.isActive('orderedList'))"
        @click="editor.chain().focus().toggleOrderedList().run()" title="Lista numerowana">1. Lista</button>
      <button type="button" :class="btnClass(editor.isActive('blockquote'))"
        @click="editor.chain().focus().toggleBlockquote().run()" title="Cytat">❝</button>
      <button type="button" :class="btnClass(editor.isActive('codeBlock'))"
        @click="editor.chain().focus().toggleCodeBlock().run()" title="Blok kodu">{ }</button>
      <span class="w-px h-5 bg-gray-300 mx-1"></span>

      <button type="button" :class="btnClass(editor.isActive('link'))" @click="setLink" title="Wstaw link">🔗 Link</button>

      <label :class="btnClass(false)" title="Wgraj obraz">
        🖼 Obraz
        <input type="file" accept="image/*" class="hidden" @change="uploadImage" />
      </label>
      <span class="w-px h-5 bg-gray-300 mx-1"></span>

      <button type="button" :class="btnClass(false)" @click="editor.chain().focus().undo().run()" title="Cofnij (Ctrl+Z)">↶</button>
      <button type="button" :class="btnClass(false)" @click="editor.chain().focus().redo().run()" title="Ponów (Ctrl+Shift+Z)">↷</button>
    </div>

    <!-- Editor -->
    <div class="px-4 py-3 max-h-[600px] overflow-y-auto">
      <EditorContent :editor="editor" />
    </div>
  </div>
</template>

<style>
.ProseMirror:focus {
  outline: none;
}
.ProseMirror p.is-editor-empty:first-child::before {
  content: 'Zacznij pisać...';
  color: #9ca3af;
  pointer-events: none;
  height: 0;
  float: left;
}
</style>
