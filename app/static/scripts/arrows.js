(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
    arrows = require("arrows-svg")
    // import arrowCreate, { DIRECTION } from '/static/node_modules/arrows-svg/'
    // import arrowCreate from '/static/node_modules/arrows-svg/dist/main.js'


    // const arrow = arrowCreate({
    //   from: document.getElementById('from'),
    //   to: document.getElementById('to'),
    // })

    // /*
    //   - arrow.node is HTMLElement
    //   - remove arrow from DOM with arrow.clear()
    // */
    // document.body.appendChild(arrow.node);

        {
        const translation_from_base_x = -0.5
        const translation_to_base_x = -1.5

        const changes = Array.from(document.querySelectorAll('.row-change'))
        const mainNode = document.querySelector('main')

        console.log(arrows)
        console.log(arrows.DIRECTION)
            
        console.log(changes)
    
        for (change of changes){
            next_changes_str = change.getAttribute("data-next-id")
            if (next_changes_str){
                next_changes = Array.from(next_changes_str.split(' '),Number);	
            } else {
                next_changes = [];
            }

            change_i = Number(change.getAttribute("data-id"))
            console.log(change_i, change, next_changes)

            for (next_change of next_changes){
                multiplier = (next_change - change_i)

                if (next_change === change_i + 1){
                    console.log("next change is consecutive")
                    // directions = [DIRECTION.BOTTOM, DIRECTION.TOP]
                    directions = ['bottom', 'top'];
                    translations = [[1, 1], [1, -1]];
                } else {
                    // directions = [DIRECTION.LEFT, DIRECTION.LEFT]
                    directions = ['left', 'left'];
                    translations = [
                        [translation_from_base_x * multiplier, 0],
                        [translation_to_base_x * multiplier, -0.1]
                    ];
                }

                from_node = change
                to_node = next_change = changes[next_change - 1]

                const arrowProps = {
                    className: 'arrow',
                    from: {
                        node: from_node,
                        direction: directions[0],
                        translation: translations[0]
                    },
                    to: {
                        node: to_node,
                        direction: directions[1],
                        translation: translations[1],
                    },
                    // head: {
                    //     func: arrows.HEAD.NORMAL
                    // }
                }
                
                console.log(arrowProps)
    
                arrow = arrows.arrowCreate(arrowProps)
                ele ment = arrow.node.firstChild

                element.classList.add(`from-${from_node.getAttribute("data-level")}`)
                element.classList.add(`to-${to_node.getAttribute("data-level")}`)

                console.log(arrow, element)
                mainNode.appendChild(arrow.node)
            }
        }
    }
},{"arrows-svg":2}],2:[function(require,module,exports){
!function(e,t){if("object"==typeof exports&&"object"==typeof module)module.exports=t();else if("function"==typeof define&&define.amd)define([],t);else{var n=t();for(var r in n)("object"==typeof exports?exports:e)[r]=n[r]}}(self,(()=>(()=>{"use strict";var e={400:(e,t,n)=>{n.r(t),n.d(t,{Component:()=>g,Fragment:()=>m,cloneElement:()=>U,createContext:()=>B,createElement:()=>p,createRef:()=>y,h:()=>p,hydrate:()=>F,isValidElement:()=>u,options:()=>o,render:()=>R,toChildArray:()=>A});var r,o,i,u,_,a,l,c={},f=[],s=/acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i;function d(e,t){for(var n in t)e[n]=t[n];return e}function h(e){var t=e.parentNode;t&&t.removeChild(e)}function p(e,t,n){var o,i,u,_={};for(u in t)"key"==u?o=t[u]:"ref"==u?i=t[u]:_[u]=t[u];if(arguments.length>2&&(_.children=arguments.length>3?r.call(arguments,2):n),"function"==typeof e&&null!=e.defaultProps)for(u in e.defaultProps)void 0===_[u]&&(_[u]=e.defaultProps[u]);return v(e,_,o,i,null)}function v(e,t,n,r,u){var _={type:e,props:t,key:n,ref:r,__k:null,__:null,__b:0,__e:null,__d:void 0,__c:null,__h:null,constructor:void 0,__v:null==u?++i:u};return null==u&&null!=o.vnode&&o.vnode(_),_}function y(){return{current:null}}function m(e){return e.children}function g(e,t){this.props=e,this.context=t}function b(e,t){if(null==t)return e.__?b(e.__,e.__.__k.indexOf(e)+1):null;for(var n;t<e.__k.length;t++)if(null!=(n=e.__k[t])&&null!=n.__e)return n.__e;return"function"==typeof e.type?b(e):null}function T(e){var t,n;if(null!=(e=e.__)&&null!=e.__c){for(e.__e=e.__c.base=null,t=0;t<e.__k.length;t++)if(null!=(n=e.__k[t])&&null!=n.__e){e.__e=e.__c.base=n.__e;break}return T(e)}}function x(e){(!e.__d&&(e.__d=!0)&&_.push(e)&&!E.__r++||a!==o.debounceRendering)&&((a=o.debounceRendering)||setTimeout)(E)}function E(){for(var e;E.__r=_.length;)e=_.sort((function(e,t){return e.__v.__b-t.__v.__b})),_=[],e.some((function(e){var t,n,r,o,i,u;e.__d&&(i=(o=(t=e).__v).__e,(u=t.__P)&&(n=[],(r=d({},o)).__v=o.__v+1,I(u,o,r,t.__n,void 0!==u.ownerSVGElement,null!=o.__h?[i]:null,n,null==i?b(o):i,o.__h),N(n,o),o.__e!=i&&T(o)))}))}function w(e,t,n,r,o,i,u,_,a,l){var s,d,h,p,y,g,T,x=r&&r.__k||f,E=x.length;for(n.__k=[],s=0;s<t.length;s++)if(null!=(p=n.__k[s]=null==(p=t[s])||"boolean"==typeof p?null:"string"==typeof p||"number"==typeof p||"bigint"==typeof p?v(null,p,null,null,p):Array.isArray(p)?v(m,{children:p},null,null,null):p.__b>0?v(p.type,p.props,p.key,p.ref?p.ref:null,p.__v):p)){if(p.__=n,p.__b=n.__b+1,null===(h=x[s])||h&&p.key==h.key&&p.type===h.type)x[s]=void 0;else for(d=0;d<E;d++){if((h=x[d])&&p.key==h.key&&p.type===h.type){x[d]=void 0;break}h=null}I(e,p,h=h||c,o,i,u,_,a,l),y=p.__e,(d=p.ref)&&h.ref!=d&&(T||(T=[]),h.ref&&T.push(h.ref,null,p),T.push(d,p.__c||y,p)),null!=y?(null==g&&(g=y),"function"==typeof p.type&&p.__k===h.__k?p.__d=a=O(p,a,e):a=P(e,p,h,x,y,a),"function"==typeof n.type&&(n.__d=a)):a&&h.__e==a&&a.parentNode!=e&&(a=b(h))}for(n.__e=g,s=E;s--;)null!=x[s]&&j(x[s],x[s]);if(T)for(s=0;s<T.length;s++)k(T[s],T[++s],T[++s])}function O(e,t,n){for(var r,o=e.__k,i=0;o&&i<o.length;i++)(r=o[i])&&(r.__=e,t="function"==typeof r.type?O(r,t,n):P(n,r,r,o,r.__e,t));return t}function A(e,t){return t=t||[],null==e||"boolean"==typeof e||(Array.isArray(e)?e.some((function(e){A(e,t)})):t.push(e)),t}function P(e,t,n,r,o,i){var u,_,a;if(void 0!==t.__d)u=t.__d,t.__d=void 0;else if(null==n||o!=i||null==o.parentNode)e:if(null==i||i.parentNode!==e)e.appendChild(o),u=null;else{for(_=i,a=0;(_=_.nextSibling)&&a<r.length;a+=1)if(_==o)break e;e.insertBefore(o,i),u=i}return void 0!==u?u:o.nextSibling}function M(e,t,n){"-"===t[0]?e.setProperty(t,n):e[t]=null==n?"":"number"!=typeof n||s.test(t)?n:n+"px"}function D(e,t,n,r,o){var i;e:if("style"===t)if("string"==typeof n)e.style.cssText=n;else{if("string"==typeof r&&(e.style.cssText=r=""),r)for(t in r)n&&t in n||M(e.style,t,"");if(n)for(t in n)r&&n[t]===r[t]||M(e.style,t,n[t])}else if("o"===t[0]&&"n"===t[1])i=t!==(t=t.replace(/Capture$/,"")),t=t.toLowerCase()in e?t.toLowerCase().slice(2):t.slice(2),e.l||(e.l={}),e.l[t+i]=n,n?r||e.addEventListener(t,i?C:H,i):e.removeEventListener(t,i?C:H,i);else if("dangerouslySetInnerHTML"!==t){if(o)t=t.replace(/xlink(H|:h)/,"h").replace(/sName$/,"s");else if("href"!==t&&"list"!==t&&"form"!==t&&"tabIndex"!==t&&"download"!==t&&t in e)try{e[t]=null==n?"":n;break e}catch(e){}"function"==typeof n||(null==n||!1===n&&-1==t.indexOf("-")?e.removeAttribute(t):e.setAttribute(t,n))}}function H(e){this.l[e.type+!1](o.event?o.event(e):e)}function C(e){this.l[e.type+!0](o.event?o.event(e):e)}function I(e,t,n,r,i,u,_,a,l){var c,f,s,h,p,v,y,b,T,x,E,O,A,P,M,D=t.type;if(void 0!==t.constructor)return null;null!=n.__h&&(l=n.__h,a=t.__e=n.__e,t.__h=null,u=[a]),(c=o.__b)&&c(t);try{e:if("function"==typeof D){if(b=t.props,T=(c=D.contextType)&&r[c.__c],x=c?T?T.props.value:c.__:r,n.__c?y=(f=t.__c=n.__c).__=f.__E:("prototype"in D&&D.prototype.render?t.__c=f=new D(b,x):(t.__c=f=new g(b,x),f.constructor=D,f.render=L),T&&T.sub(f),f.props=b,f.state||(f.state={}),f.context=x,f.__n=r,s=f.__d=!0,f.__h=[],f._sb=[]),null==f.__s&&(f.__s=f.state),null!=D.getDerivedStateFromProps&&(f.__s==f.state&&(f.__s=d({},f.__s)),d(f.__s,D.getDerivedStateFromProps(b,f.__s))),h=f.props,p=f.state,s)null==D.getDerivedStateFromProps&&null!=f.componentWillMount&&f.componentWillMount(),null!=f.componentDidMount&&f.__h.push(f.componentDidMount);else{if(null==D.getDerivedStateFromProps&&b!==h&&null!=f.componentWillReceiveProps&&f.componentWillReceiveProps(b,x),!f.__e&&null!=f.shouldComponentUpdate&&!1===f.shouldComponentUpdate(b,f.__s,x)||t.__v===n.__v){for(f.props=b,f.state=f.__s,t.__v!==n.__v&&(f.__d=!1),f.__v=t,t.__e=n.__e,t.__k=n.__k,t.__k.forEach((function(e){e&&(e.__=t)})),E=0;E<f._sb.length;E++)f.__h.push(f._sb[E]);f._sb=[],f.__h.length&&_.push(f);break e}null!=f.componentWillUpdate&&f.componentWillUpdate(b,f.__s,x),null!=f.componentDidUpdate&&f.__h.push((function(){f.componentDidUpdate(h,p,v)}))}if(f.context=x,f.props=b,f.__v=t,f.__P=e,O=o.__r,A=0,"prototype"in D&&D.prototype.render){for(f.state=f.__s,f.__d=!1,O&&O(t),c=f.render(f.props,f.state,f.context),P=0;P<f._sb.length;P++)f.__h.push(f._sb[P]);f._sb=[]}else do{f.__d=!1,O&&O(t),c=f.render(f.props,f.state,f.context),f.state=f.__s}while(f.__d&&++A<25);f.state=f.__s,null!=f.getChildContext&&(r=d(d({},r),f.getChildContext())),s||null==f.getSnapshotBeforeUpdate||(v=f.getSnapshotBeforeUpdate(h,p)),M=null!=c&&c.type===m&&null==c.key?c.props.children:c,w(e,Array.isArray(M)?M:[M],t,n,r,i,u,_,a,l),f.base=t.__e,t.__h=null,f.__h.length&&_.push(f),y&&(f.__E=f.__=null),f.__e=!1}else null==u&&t.__v===n.__v?(t.__k=n.__k,t.__e=n.__e):t.__e=S(n.__e,t,n,r,i,u,_,l);(c=o.diffed)&&c(t)}catch(e){t.__v=null,(l||null!=u)&&(t.__e=a,t.__h=!!l,u[u.indexOf(a)]=null),o.__e(e,t,n)}}function N(e,t){o.__c&&o.__c(t,e),e.some((function(t){try{e=t.__h,t.__h=[],e.some((function(e){e.call(t)}))}catch(e){o.__e(e,t.__v)}}))}function S(e,t,n,o,i,u,_,a){var l,f,s,d=n.props,p=t.props,v=t.type,y=0;if("svg"===v&&(i=!0),null!=u)for(;y<u.length;y++)if((l=u[y])&&"setAttribute"in l==!!v&&(v?l.localName===v:3===l.nodeType)){e=l,u[y]=null;break}if(null==e){if(null===v)return document.createTextNode(p);e=i?document.createElementNS("http://www.w3.org/2000/svg",v):document.createElement(v,p.is&&p),u=null,a=!1}if(null===v)d===p||a&&e.data===p||(e.data=p);else{if(u=u&&r.call(e.childNodes),f=(d=n.props||c).dangerouslySetInnerHTML,s=p.dangerouslySetInnerHTML,!a){if(null!=u)for(d={},y=0;y<e.attributes.length;y++)d[e.attributes[y].name]=e.attributes[y].value;(s||f)&&(s&&(f&&s.__html==f.__html||s.__html===e.innerHTML)||(e.innerHTML=s&&s.__html||""))}if(function(e,t,n,r,o){var i;for(i in n)"children"===i||"key"===i||i in t||D(e,i,null,n[i],r);for(i in t)o&&"function"!=typeof t[i]||"children"===i||"key"===i||"value"===i||"checked"===i||n[i]===t[i]||D(e,i,t[i],n[i],r)}(e,p,d,i,a),s)t.__k=[];else if(y=t.props.children,w(e,Array.isArray(y)?y:[y],t,n,o,i&&"foreignObject"!==v,u,_,u?u[0]:n.__k&&b(n,0),a),null!=u)for(y=u.length;y--;)null!=u[y]&&h(u[y]);a||("value"in p&&void 0!==(y=p.value)&&(y!==e.value||"progress"===v&&!y||"option"===v&&y!==d.value)&&D(e,"value",y,d.value,!1),"checked"in p&&void 0!==(y=p.checked)&&y!==e.checked&&D(e,"checked",y,d.checked,!1))}return e}function k(e,t,n){try{"function"==typeof e?e(t):e.current=t}catch(e){o.__e(e,n)}}function j(e,t,n){var r,i;if(o.unmount&&o.unmount(e),(r=e.ref)&&(r.current&&r.current!==e.__e||k(r,null,t)),null!=(r=e.__c)){if(r.componentWillUnmount)try{r.componentWillUnmount()}catch(e){o.__e(e,t)}r.base=r.__P=null,e.__c=void 0}if(r=e.__k)for(i=0;i<r.length;i++)r[i]&&j(r[i],t,n||"function"!=typeof e.type);n||null==e.__e||h(e.__e),e.__=e.__e=e.__d=void 0}function L(e,t,n){return this.constructor(e,n)}function R(e,t,n){var i,u,_;o.__&&o.__(e,t),u=(i="function"==typeof n)?null:n&&n.__k||t.__k,_=[],I(t,e=(!i&&n||t).__k=p(m,null,[e]),u||c,c,void 0!==t.ownerSVGElement,!i&&n?[n]:u?null:t.firstChild?r.call(t.childNodes):null,_,!i&&n?n:u?u.__e:t.firstChild,i),N(_,e)}function F(e,t){R(e,t,F)}function U(e,t,n){var o,i,u,_=d({},e.props);for(u in t)"key"==u?o=t[u]:"ref"==u?i=t[u]:_[u]=t[u];return arguments.length>2&&(_.children=arguments.length>3?r.call(arguments,2):n),v(e.type,_,o||e.key,i||e.ref,null)}function B(e,t){var n={__c:t="__cC"+l++,__:e,Consumer:function(e,t){return e.children(t)},Provider:function(e){var n,r;return this.getChildContext||(n=[],(r={})[t]=this,this.getChildContext=function(){return r},this.shouldComponentUpdate=function(e){this.props.value!==e.value&&n.some(x)},this.sub=function(e){n.push(e);var t=e.componentWillUnmount;e.componentWillUnmount=function(){n.splice(n.indexOf(e),1),t&&t.call(e)}}),e.children}};return n.Provider.__=n.Consumer.contextType=n}r=f.slice,o={__e:function(e,t,n,r){for(var o,i,u;t=t.__;)if((o=t.__c)&&!o.__)try{if((i=o.constructor)&&null!=i.getDerivedStateFromError&&(o.setState(i.getDerivedStateFromError(e)),u=o.__d),null!=o.componentDidCatch&&(o.componentDidCatch(e,r||{}),u=o.__d),u)return o.__E=o}catch(t){e=t}throw e}},i=0,u=function(e){return null!=e&&void 0===e.constructor},g.prototype.setState=function(e,t){var n;n=null!=this.__s&&this.__s!==this.state?this.__s:this.__s=d({},this.state),"function"==typeof e&&(e=e(d({},n),this.props)),e&&d(n,e),null!=e&&this.__v&&(t&&this._sb.push(t),x(this))},g.prototype.forceUpdate=function(e){this.__v&&(this.__e=!0,e&&this.__h.push(e),x(this))},g.prototype.render=m,_=[],E.__r=0,l=0},396:(e,t,n)=>{n.r(t),n.d(t,{useCallback:()=>w,useContext:()=>O,useDebugValue:()=>A,useEffect:()=>g,useErrorBoundary:()=>P,useId:()=>M,useImperativeHandle:()=>x,useLayoutEffect:()=>b,useMemo:()=>E,useReducer:()=>m,useRef:()=>T,useState:()=>y});var r,o,i,u,_=n(400),a=0,l=[],c=[],f=_.options.__b,s=_.options.__r,d=_.options.diffed,h=_.options.__c,p=_.options.unmount;function v(e,t){_.options.__h&&_.options.__h(o,e,a||t),a=0;var n=o.__H||(o.__H={__:[],__h:[]});return e>=n.__.length&&n.__.push({__V:c}),n.__[e]}function y(e){return a=1,m(k,e)}function m(e,t,n){var i=v(r++,2);if(i.t=e,!i.__c&&(i.__=[n?n(t):k(void 0,t),function(e){var t=i.__N?i.__N[0]:i.__[0],n=i.t(t,e);t!==n&&(i.__N=[n,i.__[1]],i.__c.setState({}))}],i.__c=o,!o.u)){o.u=!0;var u=o.shouldComponentUpdate;o.shouldComponentUpdate=function(e,t,n){if(!i.__c.__H)return!0;var r=i.__c.__H.__.filter((function(e){return e.__c}));if(r.every((function(e){return!e.__N})))return!u||u.call(this,e,t,n);var o=!1;return r.forEach((function(e){if(e.__N){var t=e.__[0];e.__=e.__N,e.__N=void 0,t!==e.__[0]&&(o=!0)}})),!(!o&&i.__c.props===e)&&(!u||u.call(this,e,t,n))}}return i.__N||i.__}function g(e,t){var n=v(r++,3);!_.options.__s&&S(n.__H,t)&&(n.__=e,n.i=t,o.__H.__h.push(n))}function b(e,t){var n=v(r++,4);!_.options.__s&&S(n.__H,t)&&(n.__=e,n.i=t,o.__h.push(n))}function T(e){return a=5,E((function(){return{current:e}}),[])}function x(e,t,n){a=6,b((function(){return"function"==typeof e?(e(t()),function(){return e(null)}):e?(e.current=t(),function(){return e.current=null}):void 0}),null==n?n:n.concat(e))}function E(e,t){var n=v(r++,7);return S(n.__H,t)?(n.__V=e(),n.i=t,n.__h=e,n.__V):n.__}function w(e,t){return a=8,E((function(){return e}),t)}function O(e){var t=o.context[e.__c],n=v(r++,9);return n.c=e,t?(null==n.__&&(n.__=!0,t.sub(o)),t.props.value):e.__}function A(e,t){_.options.useDebugValue&&_.options.useDebugValue(t?t(e):e)}function P(e){var t=v(r++,10),n=y();return t.__=e,o.componentDidCatch||(o.componentDidCatch=function(e,r){t.__&&t.__(e,r),n[1](e)}),[n[0],function(){n[1](void 0)}]}function M(){var e=v(r++,11);if(!e.__){for(var t=o.__v;null!==t&&!t.__m&&null!==t.__;)t=t.__;var n=t.__m||(t.__m=[0,0]);e.__="P"+n[0]+"-"+n[1]++}return e.__}function D(){for(var e;e=l.shift();)if(e.__P&&e.__H)try{e.__H.__h.forEach(I),e.__H.__h.forEach(N),e.__H.__h=[]}catch(t){e.__H.__h=[],_.options.__e(t,e.__v)}}_.options.__b=function(e){o=null,f&&f(e)},_.options.__r=function(e){s&&s(e),r=0;var t=(o=e.__c).__H;t&&(i===o?(t.__h=[],o.__h=[],t.__.forEach((function(e){e.__N&&(e.__=e.__N),e.__V=c,e.__N=e.i=void 0}))):(t.__h.forEach(I),t.__h.forEach(N),t.__h=[])),i=o},_.options.diffed=function(e){d&&d(e);var t=e.__c;t&&t.__H&&(t.__H.__h.length&&(1!==l.push(t)&&u===_.options.requestAnimationFrame||((u=_.options.requestAnimationFrame)||C)(D)),t.__H.__.forEach((function(e){e.i&&(e.__H=e.i),e.__V!==c&&(e.__=e.__V),e.i=void 0,e.__V=c}))),i=o=null},_.options.__c=function(e,t){t.some((function(e){try{e.__h.forEach(I),e.__h=e.__h.filter((function(e){return!e.__||N(e)}))}catch(n){t.some((function(e){e.__h&&(e.__h=[])})),t=[],_.options.__e(n,e.__v)}})),h&&h(e,t)},_.options.unmount=function(e){p&&p(e);var t,n=e.__c;n&&n.__H&&(n.__H.__.forEach((function(e){try{I(e)}catch(e){t=e}})),n.__H=void 0,t&&_.options.__e(t,n.__v))};var H="function"==typeof requestAnimationFrame;function C(e){var t,n=function(){clearTimeout(r),H&&cancelAnimationFrame(t),setTimeout(e)},r=setTimeout(n,100);H&&(t=requestAnimationFrame(n))}function I(e){var t=o,n=e.__c;"function"==typeof n&&(e.__c=void 0,n()),o=t}function N(e){var t=o;e.__c=e.__(),o=t}function S(e,t){return!e||e.length!==t.length||t.some((function(t,n){return t!==e[n]}))}function k(e,t){return"function"==typeof t?t(e):t}},515:function(e,t,n){var r=this&&this.__assign||function(){return r=Object.assign||function(e){for(var t,n=1,r=arguments.length;n<r;n++)for(var o in t=arguments[n])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},r.apply(this,arguments)};Object.defineProperty(t,"__esModule",{value:!0}),t.autoAnchorWithPoint=t.createAnchorWithPoint=t.castToAnchor=void 0;var o=n(773),i=n(312);t.castToAnchor=function(e){return"function"==typeof e||e instanceof HTMLElement?{node:e}:e},t.createAnchorWithPoint=function(e){var n=t.castToAnchor(e),u=function(e){var t=o.default(e.node);if(!t)throw new Error("Point is null or not contained by the document body. Check if 'from'/'to' exists, was added to the DOM (and not removed since).");var n=t.getBoundingClientRect(),r=n.x||n.left,u=n.y||n.top;switch(e.direction){case i.DIRECTION.TOP_LEFT:return{x:r,y:u};case i.DIRECTION.TOP:return{x:r+n.width/2,y:u};case i.DIRECTION.TOP_RIGHT:return{x:r+n.width,y:u};case i.DIRECTION.RIGHT:return{x:r+n.width,y:u+n.height/2};case i.DIRECTION.BOTTOM_LEFT:return{x:r,y:u+n.height};case i.DIRECTION.BOTTOM:return{x:r+n.width/2,y:u+n.height};case i.DIRECTION.BOTTOM_RIGHT:return{x:r+n.width,y:u+n.height};case i.DIRECTION.LEFT:return{x:r,y:u+n.height/2};default:return{x:r+n.width/2,y:u+n.height/2}}}(n);return r(r({},n),u)},t.autoAnchorWithPoint=function(e,n){if(e.translation&&e.direction)return e;var o=r({},e),u=function(e,t){!function(e){o.direction||(o.direction=e)}(e),function(e){o.translation||(o.translation=e)}(t)};return Math.abs(e.x-n.x)>Math.abs(e.y-n.y)?e.x<n.x?u(i.DIRECTION.RIGHT,[.3,0]):u(i.DIRECTION.LEFT,[-.3,0]):e.y<n.y?u(i.DIRECTION.BOTTOM,[0,.3]):u(i.DIRECTION.TOP,[0,-.3]),t.createAnchorWithPoint(o)}},940:function(e,t,n){var r=this&&this.__assign||function(){return r=Object.assign||function(e){for(var t,n=1,r=arguments.length;n<r;n++)for(var o in t=arguments[n])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},r.apply(this,arguments)};Object.defineProperty(t,"__esModule",{value:!0}),t.Arrow=void 0;var o=n(400),i=n(396),u=n(296),_=n(778),a=n(515),l=n(981);t.Arrow=function(e){var t=e.className,n=e.head,a=e.from,c=e.to,f=e.forwardRef,s=e.updateDelay,d=i.useState((function(){return _.default(a,c,n)})),h=d[0],p=d[1];return i.useEffect((function(){return u.default(a,c,{update:function(){return p(_.default(a,c,n))},updateDelay:s}).clear}),[a,n,c,s]),o.h("svg",{className:t,style:{top:h.offset.y,left:h.offset.x,position:"fixed"},width:h.size.width,height:h.size.height,ref:f},o.h("path",{className:t+"__path",d:h.pathCommands}),h.heads.map((function(e){if(!e.node)return null;var n={className:t+"__head "+t+"__head--"+e.id,transform:l.headTransformCSS(e)};if("string"==typeof e.node)return o.h("g",r({key:e.id},n,{dangerouslySetInnerHTML:{__html:e.node}}));var i=e.node;return i.tagName?o.h("g",r({},n,{dangerouslySetInnerHTML:{__html:i.outerHTML}})):o.h("g",r({key:e.id},n),e.node)})))},t.default=function(e){var n=e.className,r=void 0===n?"arrow":n,i=e.head,u=void 0===i?l.HEAD.THIN:i,_=e.from,c=e.to,f=e.updateDelay,s=o.createRef(),d=document.createDocumentFragment();if(!_)throw new Error("undefined from, try to pass it as from={() => ...}");if(!c)throw new Error("undefined to, try to pass it as to={() => ...}");return o.render(o.h(t.Arrow,{className:r,head:u,from:a.castToAnchor(_),to:a.castToAnchor(c),forwardRef:s,updateDelay:f}),d),{node:d,clear:function(){var e=s.current,t=e.parentNode;t&&t.removeChild(e)}}}},778:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(515),o=n(240),i=n(981),u=n(945);t.default=function(e,t,n){var _=i.prepareHeads(n),a=i.calculateHeadsPadding(_),l=r.createAnchorWithPoint(e),c=r.createAnchorWithPoint(t),f=o.produceContainer(r.autoAnchorWithPoint(l,c),r.autoAnchorWithPoint(c,l),a),s=u.pathListBezier(f,a),d=i.assignPathToHeads(_,s),h=u.convertPathToSVG(s),p=function(e,t){var n=u.pathReducer(e,(function(e,t){return{x:Math.max(e.x,t.x),y:Math.max(e.y,t.y)}}));return{width:n.x+2*t.width,height:n.y+2*t.height}}(s,a),v=function(e,t,n){var r=function(t){return Math.min(e[0][t]-n.width,e[3][t]-n.height)};return{x:t.position.x-r("x")-n.width,y:t.position.y-r("y")-n.height}}(s,f,a);return{pathCommands:h,size:p,offset:v,heads:d}}},312:(e,t)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.DIRECTION=t.HEAD_DEFAULT_SIZE=void 0,t.HEAD_DEFAULT_SIZE=10,t.DIRECTION={TOP_LEFT:"top-left",TOP:"top",TOP_RIGHT:"top-right",RIGHT:"right",BOTTOM_LEFT:"bottom-left",BOTTOM:"bottom",BOTTOM_RIGHT:"bottom-right",LEFT:"left"}},240:function(e,t,n){var r=this&&this.__assign||function(){return r=Object.assign||function(e){for(var t,n=1,r=arguments.length;n<r;n++)for(var o in t=arguments[n])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},r.apply(this,arguments)};Object.defineProperty(t,"__esModule",{value:!0}),t.produceContainer=void 0;var o=n(134),i=function(e,t,n){return o.pointSubtraction(r(r({},e),{x:e.x-t.x,y:e.y-t.y}),{x:2*-n.width,y:2*-n.height})};t.produceContainer=function(e,t,n){var r={x:Math.min(e.x,t.x),y:Math.min(e.y,t.y)},o=i(e,r,n),u=i(t,r,n),_=function(e,t){return{width:Math.max(e.x,t.x),height:Math.max(e.y,t.y)}}(o,u);return{position:r,relativeFrom:o,relativeTo:u,size:_}}},382:function(e,t,n){var r=this&&this.__assign||function(){return r=Object.assign||function(e){for(var t,n=1,r=arguments.length;n<r;n++)for(var o in t=arguments[n])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},r.apply(this,arguments)};Object.defineProperty(t,"__esModule",{value:!0}),t.headTransformCSS=t.assignPathToHeads=t.calculateHeadsPadding=t.prepareHeads=t.prepareHeadNode=void 0;var o=n(740),i=function(e){return Math.round(1e3*e)/1e3},u=function(e){if("string"==typeof e){var t=e;return o.default[t]}if("object"==typeof e){if("function"==typeof e.func)return e.func;if("string"==typeof e.func)return u(e.func)}if("function"==typeof e)return e;throw new Error("head type is invalid")};t.prepareHeadNode=function(e){var t=u(e)(e);if(!t||!t.width||!t.height)throw new Error("head function should return { node, width, height }");return"object"==typeof e&&Object.assign(t,e),t.distance||(t.distance=1),t},t.prepareHeads=function(e){return(Array.isArray(e)?e:[e]).map(t.prepareHeadNode)},t.calculateHeadsPadding=function(e){return e.reduce((function(e,t){var n={width:e.width,height:e.height};return t.width>n.width&&(n.width=t.width),t.height>n.height&&(n.height=t.height),n}),{width:0,height:0})},t.assignPathToHeads=function(e,t){return e.map((function(e,n){return r(r(r({id:n},e),function(e,t){var n=e.distance,r=function(e){return Math.pow(1-n,2)*(t[1][e]-t[0][e])+2*n*(1-n)*(t[2][e]-t[1][e])+n*n*(t[3][e]-t[2][e])},o=r("x"),u=r("y"),_=i(-Math.atan2(o,u)+.5*Math.PI);return{degree:i(_*(180/Math.PI)),radius:_}}(e,t)),function(e,t){var n=e.distance,r=function(e){return Math.pow(1-n,3)*t[0][e]+3*n*Math.pow(1-n,2)*t[1][e]+3*n*n*(1-n)*t[2][e]+n*n*n*t[3][e]};return{x:r("x"),y:r("y")}}(e,t))}))},t.headTransformCSS=function(e){return"rotate("+e.degree+", "+e.x+", "+e.y+"), translate("+e.x+", "+e.y+")"}},981:function(e,t,n){var r=this&&this.__createBinding||(Object.create?function(e,t,n,r){void 0===r&&(r=n),Object.defineProperty(e,r,{enumerable:!0,get:function(){return t[n]}})}:function(e,t,n,r){void 0===r&&(r=n),e[r]=t[n]}),o=this&&this.__exportStar||function(e,t){for(var n in e)"default"===n||Object.prototype.hasOwnProperty.call(t,n)||r(t,e,n)};Object.defineProperty(t,"__esModule",{value:!0}),t.HEAD=void 0,o(n(382),t);var i=n(740);Object.defineProperty(t,"HEAD",{enumerable:!0,get:function(){return i.default}})},380:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(400),o=n(312);t.default=function(e){var t=e.size,n=void 0===t?o.HEAD_DEFAULT_SIZE:t;return{node:r.h("g",{transform:"translate(-"+n+", 0)"},r.h("path",{d:"M"+-n+" 0 L0 "+-n+" L"+n+" 0 L0 "+n+" Z"})),width:n,height:n}}},796:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(400),o=n(312);t.default=function(e){var t=e.size,n=void 0===t?o.HEAD_DEFAULT_SIZE:t;return{node:r.h("g",{transform:"translate(-"+n+", 0)"},r.h("circle",{cx:0,cy:0,r:n})),width:n,height:n}}},591:(e,t)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.default=function(e){var t=e.src,n=e.width,r=e.height;if(!t||!n||!r)throw new Error("image requires src, height, width");var o=document.createElementNS("http://www.w3.org/2000/svg","image");return o.setAttributeNS(null,"width",String(n)),o.setAttributeNS(null,"height",String(r)),o.setAttributeNS(null,"x",String(-n)),o.setAttributeNS(null,"y",String(-r/2)),o.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",t),{node:o,width:n,height:r}}},740:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(380),o=n(796),i=n(591),u=n(729),_=n(777),a=n(263),l=n(549),c=n(579),f={diamond:r.default,DIAMOND:r.default,dot:o.default,DOT:o.default,image:i.default,IMAGE:i.default,none:a.default,NONE:a.default,inv:u.default,INV:u.default,normal:_.default,NORMAL:_.default,thin:l.default,THIN:l.default,vee:c.default,VEE:c.default};t.default=f},729:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(400),o=n(312);t.default=function(e){var t=e.size,n=void 0===t?o.HEAD_DEFAULT_SIZE:t;return{node:r.h("path",{d:"M"+-n+" 0 L0 "+-n+" L0 "+n+" Z"}),width:n,height:n}}},263:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(312);t.default=function(){return{node:null,width:r.HEAD_DEFAULT_SIZE,height:r.HEAD_DEFAULT_SIZE}}},777:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(400),o=n(312);t.default=function(e){var t=e.size,n=void 0===t?o.HEAD_DEFAULT_SIZE:t;return{node:r.h("path",{d:"M"+-n+" "+-n+" L0 0 L"+-n+" "+n+" Z"}),width:n,height:n}}},549:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(400),o=n(312);t.default=function(e){var t=e.size,n=void 0===t?o.HEAD_DEFAULT_SIZE:t;return{node:r.h("g",null,r.h("line",{x1:-n,y1:-n,x2:0,y2:0}),r.h("line",{x1:0,y1:0,x2:-n,y2:n})),width:n,height:n}}},579:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(400),o=n(312);t.default=function(e){var t=e.size,n=void 0===t?o.HEAD_DEFAULT_SIZE:t;return{node:r.h("g",{transform:"translate(-"+n+", 0)"},r.h("path",{d:"M"+-n+" "+-n+" L"+n+" 0 L"+-n+" "+n+" L0 0 Z"})),width:n,height:n}}},773:(e,t)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.default=function(e){var t="function"==typeof e?e():e;return document.body.contains(t)?t:null}},202:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.assignArrowCreate=void 0;var r=n(940);t.assignArrowCreate=function(e){e&&(e.arrowCreate=r.default)}},296:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0});var r=n(773),o=["x","y","width","height"],i={from:null,to:null},u=function(e,t){var n=t.getBoundingClientRect();return e?{equal:!o.some((function(t){return e[t]!==n[t]})),rect:n}:{equal:!1,rect:n}};t.default=function(e,t,n){var o,_=n.updateDelay,a=void 0===_?0:_,l=n.update,c=i,f=function(){var n=r.default(e.node),o=r.default(t.node);if(n&&o){var _=function(e,t,n){var r=u(e.from,t),o=u(e.to,n);return r.equal&&o.equal?null:{from:r.rect,to:o.rect}}(c,n,o);_&&(c!==i&&l(),c=_)}};if(a){var s=setInterval(f,a);return{clear:function(){return clearInterval(s)}}}var d=function(){f(),o=requestAnimationFrame(d)};return o=requestAnimationFrame(d),{clear:function(){return cancelAnimationFrame(o)}}}},945:(e,t,n)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.pathListBezier=t.pathReducer=t.convertPathToSVG=void 0;var r=n(134);t.convertPathToSVG=function(e){var t=["M"];return t.push(r.pointToArray(e[0])),t.push("C"),t.push(r.pointToArray(e[1])),t.push(","),t.push(r.pointToArray(e[2])),t.push(","),t.push(r.pointToArray(e[3])),t.flat().join(" ").replace(/ ,/g,",")},t.pathReducer=function(e,t){return e.reduce((function(e,n){return t(e,n)}))},t.pathListBezier=function(e,n){var o=[];return o.push(e.relativeFrom),o.push(r.pointBezier(e.relativeFrom,e.size)),o.push(r.pointBezier(e.relativeTo,e.size)),o.push(e.relativeTo),function(e,n){var r=t.pathReducer(e,(function(e,t){return{x:Math.min(e.x,t.x),y:Math.min(e.y,t.y)}}));return e.map((function(e){return{x:e.x-r.x+n.width,y:e.y-r.y+n.height}}))}(o,n)}},134:function(e,t){var n=this&&this.__assign||function(){return n=Object.assign||function(e){for(var t,n=1,r=arguments.length;n<r;n++)for(var o in t=arguments[n])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},n.apply(this,arguments)};Object.defineProperty(t,"__esModule",{value:!0}),t.pointSubtraction=t.pointBezier=t.pointToArray=void 0,t.pointToArray=function(e){return[e.x,e.y]},t.pointBezier=function(e,t){return{x:e.x+t.width*e.translation[0],y:e.y+t.height*e.translation[1]}},t.pointSubtraction=function(e,t){return n(n({},e),{x:e.x-t.x,y:e.y-t.y})}}},t={};function n(r){var o=t[r];if(void 0!==o)return o.exports;var i=t[r]={exports:{}};return e[r].call(i.exports,i,i.exports,n),i.exports}n.d=(e,t)=>{for(var r in t)n.o(t,r)&&!n.o(e,r)&&Object.defineProperty(e,r,{enumerable:!0,get:t[r]})},n.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})};var r={};return(()=>{var e=r;Object.defineProperty(e,"__esModule",{value:!0}),e.HEAD=e.DIRECTION=e.arrowCreate=void 0;var t=n(202),o=n(940);e.arrowCreate=o.default,t.assignArrowCreate(window),e.default=o.default;var i=n(312);Object.defineProperty(e,"DIRECTION",{enumerable:!0,get:function(){return i.DIRECTION}});var u=n(981);Object.defineProperty(e,"HEAD",{enumerable:!0,get:function(){return u.HEAD}})})(),r})()));
},{}]},{},[1]);
