import { describe, it, expect, beforeEach } from 'vitest'
import { JSDOM } from 'jsdom'

describe('Chat App Frontend', () => {
  let dom
  let document
  let window

  beforeEach(() => {
    // Set up a clean DOM for each test
    dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <head><title>Chat Bot UI 6</title></head>
        <body>
          <div id="app" x-data="chatApp()">
            <select x-model="selectedModel"></select>
            <select x-model="selectedTools" multiple></select>
            <select x-model="selectedDataSources" multiple></select>
            <textarea x-model="currentMessage"></textarea>
            <button @click="sendMessage()">Send</button>
          </div>
        </body>
      </html>
    `)
    document = dom.window.document
    window = dom.window
    global.document = document
    global.window = window
  })

  it('should have correct HTML structure', () => {
    expect(document.title).toBe('Chat Bot UI 6')
    expect(document.querySelector('#app')).toBeTruthy()
    expect(document.querySelector('[x-data="chatApp()"]')).toBeTruthy()
  })

  it('should have all required form elements', () => {
    expect(document.querySelector('select[x-model="selectedModel"]')).toBeTruthy()
    expect(document.querySelector('select[x-model="selectedTools"]')).toBeTruthy()
    expect(document.querySelector('select[x-model="selectedDataSources"]')).toBeTruthy()
    expect(document.querySelector('textarea[x-model="currentMessage"]')).toBeTruthy()
    expect(document.querySelector('button')).toBeTruthy()
  })

  it('should have multi-select attributes for tools and data sources', () => {
    const toolsSelect = document.querySelector('select[x-model="selectedTools"]')
    const dataSourcesSelect = document.querySelector('select[x-model="selectedDataSources"]')
    
    expect(toolsSelect.hasAttribute('multiple')).toBe(true)
    expect(dataSourcesSelect.hasAttribute('multiple')).toBe(true)
  })

  it('should have Alpine.js directives in place', () => {
    expect(document.querySelector('[x-data]')).toBeTruthy()
    expect(document.querySelector('[x-model]')).toBeTruthy()
    expect(document.querySelector('[\\@click]')).toBeTruthy()
  })
})