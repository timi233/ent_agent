import { render } from '@testing-library/vue'
import BaseCard from '../BaseCard.vue'

describe('BaseCard', () => {
  it('renders title and slot content', () => {
    const { getByText } = render(BaseCard, {
      props: { title: '测试标题' },
      slots: {
        default: '<p>内容区</p>'
      }
    })

    expect(getByText('测试标题')).toBeInTheDocument()
    expect(getByText('内容区')).toBeInTheDocument()
  })
})
