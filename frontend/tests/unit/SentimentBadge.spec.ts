import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SentimentBadge from '../../src/components/SentimentBadge.vue'

describe('SentimentBadge', () => {
  it('renders the sentiment and rounded confidence score', () => {
    const wrapper = mount(SentimentBadge, {
      props: { sentiment: 'positive', confidence: 0.934 },
    })

    expect(wrapper.classes()).toContain('sentiment-positive')
    expect(wrapper.text()).toContain('positive')
    expect(wrapper.text()).toContain('93 %')
  })

  it('does not render a confidence score when it is omitted', () => {
    const wrapper = mount(SentimentBadge, {
      props: { sentiment: 'neutral' },
    })

    expect(wrapper.find('small').exists()).toBe(false)
  })
})
