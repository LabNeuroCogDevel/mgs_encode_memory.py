var app = new Vue({
    el: '#disp',
    data: {
       cur_idx: 0,
       cur_slide: 'saw' 
       //cur_img: 'img/A/inside/sun_aaloiwdypreqzwnn.png'
       cur_img: 'img/example.png'
    },
    methods: {
       side: function(pos) {
          console.log('side ',pos)
          this.cur_slide = 'saw' 
          this.cur_idx += 1
       },
       saw: function(known) {
          console.log('saw ',known)
          if(known < 0) {
            this.cur_idx += 1
          } else {
            this.cur_slide = 'side' 
          }
       }
    }
})
